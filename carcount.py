import jetson.inference
import jetson.utils

import argparse
import sys

# custom model paths
model_path = 'model/ssd-mobilenet.onnx'
label_path = 'model/labels.txt'

detect_threshold = '0.3'

total_detections = 0

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

# process frames until the user exits
while True:
	# capture the next image
	img = input.Capture()

	# detect objects in the image (with overlay)
	detections = net.Detect(img, overlay=opt.overlay)

	# print the detections
	# print("detected {:d} objects in image".format(len(detections)))
	total_detections += len(detections)
	for detection in detections:
		print(detection.Center)

	# render the image
	output.Render(img)

	# update the title bar
	output.SetStatus("{:s} | Network {:.0f} FPS | Total detections: {:}".format('car network xd', net.GetNetworkFPS(), total_detections))

	# print out performance info
	#  net.PrintProfilerTimes()

	# exit on input/output EOS
	if not input.IsStreaming() or not output.IsStreaming():
		break