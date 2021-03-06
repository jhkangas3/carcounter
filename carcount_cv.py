'''
Computer-vision based car counter.
Author: Juho Kangas
'''

import jetson.inference
import jetson.utils

import argparse
import sys
# Import math for square root for distance calculation
import math
# For timestamping the detections to a text file
from datetime import datetime
# Opencv dependencies
import cv2
import numpy

# custom model paths
model_path = 'model/ssd-mobilenet.onnx'
label_path = 'model/labels.txt'

# Set the minimum detection certainty threshold
detect_threshold = '0.3'

total_detections = 0

previous_detections = 0
current_detections = 0

prev_count = 0

# detection area coordinate definitions
x1 = 600
x2 = 680
y1 = 300
y2 = 700

# drawn detection box
color = (255,0,255,200)
thick = 3


# allowed distance between detection centerpoints between frames, higher than this counts as a new car
distance_cutoff = 60
# will hold the center points of detections, 2 frames backwards memory
center_list = []
# center_list_1 = []
# center_list_2 = []

# parse the command line
parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.")

parser.add_argument("input_URI", type=str, default="/dev/video0", nargs='?', help="URI of the input stream")
parser.add_argument("output_URI", type=str, default="", nargs='?', help="URI of the output stream")
parser.add_argument("--overlay", type=str, default="box,labels,conf", help="detection overlay flags (e.g. --overlay=box,labels,conf)\nvalid combinations are:  'box', 'labels', 'conf', 'none'")

# Open a file to save detections
file = open("detections.txt", 'w')


try:
	opt = parser.parse_known_args()[0]
except:
	print("")
	parser.print_help()
	sys.exit(0)

# load the object detection network
net = jetson.inference.detectNet(argv=['--model='+model_path, '--labels='+label_path, '--input-blob=input_0', '--output-cvg=scores', '--output-bbox=boxes', '--threshold='+detect_threshold])

# create video sources & outputs
input = jetson.utils.videoSource(opt.input_URI, argv=sys.argv)
output = jetson.utils.videoOutput(opt.output_URI, argv=sys.argv)

# function to calculate distance between 2 points
def distance(x1, y1, x2, y2):
	return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

# process frames until the user exits
while True:
	# capture the next image
	img = input.Capture()

	# detect objects in the image (with overlay)
	detections = net.Detect(img, overlay=opt.overlay)




	# current_detections = len(detections)
	previous_detections = len(center_list)


	count = 0
	for detection in detections:
		for centerpoints in center_list:
			if distance(detection.Center[0], detection.Center[1], centerpoints[0], centerpoints[1]) < distance_cutoff:
				count += 1



	if count < prev_count:
		total_detections += prev_count - count		
		# print the detections when new is added
		print("Cars counted: {0}".format(total_detections))
		file.write("{0},{1} \n".format(total_detections, datetime.now()))

	prev_count = count

	center_list = []
	
	
	for detection in detections:
		if x1 < detection.Center[0] < x2 :
			# save detection info for next loop if they are within the detection box
			center_list.append(detection.Center)

	# Draw a box around the intended detection zone
	jetson.utils.cudaDrawLine(img, (x1,y1),(x2,y1), color, thick)
	jetson.utils.cudaDrawLine(img, (x1,y1),(x1,y2), color, thick)
	jetson.utils.cudaDrawLine(img, (x1,y2),(x2,y2), color, thick)
	jetson.utils.cudaDrawLine(img, (x2,y1),(x2,y2), color, thick)

    # Frame converted to numpy array so cv2 can be used
	array = jetson.utils.cudaToNumpy(img)

	# Text is written on the frame to display the amount of passed cars
	font                   = cv2.FONT_HERSHEY_SIMPLEX
	bottomLeftCornerOfText = (10,100)
	fontScale              = 1
	fontColor              = (255,150,150)
	lineType               = 2

	cv2.putText(array,'Car count: {0}'.format(total_detections), 
		bottomLeftCornerOfText, 
		font, 
		fontScale,
		fontColor,
		lineType)

	# Conversion back to cuda frame for rendering
	img = jetson.utils.cudaFromNumpy(array)

	# render the image
	output.Render(img)

	# update the title bar
	output.SetStatus("{:s} | Network {:.0f} FPS | Total detections: {:}".format('car network xd', net.GetNetworkFPS(), total_detections))


	# exit on input/output EOS
	if not input.IsStreaming() or not output.IsStreaming():
		file.close()
		break