'''
Computer-vision based car counter.
Author: Juho Kangas
'''

import jetson.inference
import jetson.utils

import argparse
import sys

import math

# custom model paths
model_path = 'model/ssd-mobilenet.onnx'
label_path = 'model/labels.txt'

detect_threshold = '0.3'

total_detections = 0

previous_detections = 0
current_detections = 0

prev_count = 0

# detection area coordinate definitions
x1 = 600
x2 = 720
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

	# if count < previous_detections:
	# 	for detection in detections:
	# 		for centerpoints in center_list_1:
	# 			if distance(detection.Center[0], detection.Center[1], centerpoints[0], centerpoints[1]) < distance_cutoff:
	# 				count += 1

	if count < prev_count:
		total_detections += prev_count - count		
		# print the detections when new is added
		print("Cars counted: {0}".format(total_detections))

	prev_count = count
	# pass on the data for next loops, clear current data
	# center_list_2 = center_list_1
	# center_list_1 = center_list
	center_list = []
	

	# print("IN BOX {0}, COUNT {1}".format(previous_detections, count))
	
	for detection in detections:
		if x1 < detection.Center[0] < x2 :
			# save detection info for next loop if they are within the detection box
			center_list.append(detection.Center)

	jetson.utils.cudaDrawLine(img, (x1,y1),(x2,y1), color, thick)
	jetson.utils.cudaDrawLine(img, (x1,y1),(x1,y2), color, thick)
	jetson.utils.cudaDrawLine(img, (x1,y2),(x2,y2), color, thick)
	jetson.utils.cudaDrawLine(img, (x2,y1),(x2,y2), color, thick)

	# render the image
	output.Render(img)

	# update the title bar
	output.SetStatus("{:s} | Network {:.0f} FPS | Total detections: {:}".format('car network xd', net.GetNetworkFPS(), total_detections))


	# exit on input/output EOS
	if not input.IsStreaming() or not output.IsStreaming():
		break