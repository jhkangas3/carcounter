# Computer Vision car counter

This program will count the amount of cars passing the camera.

Demo video of the program can be opened by clicking the picture underneath.

[![Demo video](https://img.youtube.com/vi/UZwzsyBBVkY/0.jpg)](https://youtu.be/UZwzsyBBVkY)

The program uses computer vision and AI to detect cars, count the amount of cars passed, and . Object detection model for this program was trained for this specific purpose. It knows only one class, which is "car". Training material was gathered using the same camera and in the same position as the demo video shows. 1000+ photos were gathered during various times of day and various weathers in slightly varying camera orientations. Taken pictures were used to re-train SSD-mobilenet-V2 to 50 epochs. Trained model reached total loss of ~1.6, which could be potentially improved by gathering more data, but it was found to be sufficient when tracking cars through a narrow slice of the camera view. The model was converted to ONNX format. The model created for this purpose is optimized to work with camera in specific position looking through my window, so results may vary if tried elsewhere.


Two versions of the program are supplied, carcount.py, and carcount_cv.py. The difference is that first one prints the car detections into the terminal, and displays the count in the status bar of the video. The second one uses openCV to draw the counter on the video frames. In either case, the detections with timestamps are stored in a text file called "detections.txt" for to make statistics.

The initial thought to counting, was to track the cars the for the entire travel past the camera, but that became soon very problematic due to the lack of robustness of the model when the cars aren't detected in every frame as they pass the camera. The solution to this was to count the cars passing through a single narrow vertical slice of the frame. The region of interest is drawn on the screen with a pink box. 
When a car enters the region, the center point of the detection is saved to a list. Next frame, the distance from current detections are measured against previous detections. If the distance calculated is less than a set distance temporary counter goes up by 1. When this counter goes down, the actual car counter gets incremented. This slightly filters the result, as detections lasting for only 1 frame do not get counted. 


This approach works as long as the car gets constantly detected through the region of interest. Sometimes, when the detection is not constant, a single car can count as multiple cars. Other sources of problems are cause by big cars and trucks and sometimes ordinary cars have multiple detection boxed overlapping. Making separate classes for trucks and bikes and buses were excluded from this project due to the relatively very small number of them passing the camera, making the gathering of training material difficult.


## Requirements

Nvidia Jetson Nano

Compatible webcam

Jetson inference container

Python libraries: numpy, opencv2



## Usage

Open jetson-inference folder, pull the project inside a folder mounted for the docker and run the docker
```
cd jetson-inference/data
git pull https://gitlab.com/jhkangas3/carcounter.git
../docker/run.sh
```
Change into folder containing the project
```
cd data/carcounter
```

Run the program
```
python3 carcount.py (optional camera argument, default /dev/video0)
```



Run the program with statistics drawn on screen using 
```
python3 carcount_v2.py (optional camera argument, default /dev/video0)
```

If openCV import fails, run
```
export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1
```


## Author
Juho Kangas
