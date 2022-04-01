# Computer Vision car counter

This program will count the amount of cars passing the camera.

![](my_video2.mp4)

The program uses computer vision and AI to detect cars. Object detection model for this program was trained for this specific purpose. It knows only one class, which is "car". Training material was gathered using the same camera and in the same position as the demo video shows. 500+ photos were gathered during various times of day and various weathers and they were used to re-train SSD-mobilenet-V2 to 65 epochs. The downside of this approach, is that currrently the models know how cars look like from this very specific angle, and even small variations in the angle cause significant drop in detection quality, causing duplicate detections, or lack of detections. One possible, and probably most important  further development would be to increase and diversify the training material to increase the detection quality.


Right now, there are two versions, carcount.py, and carcount_v2.py. The difference is that first one prints the car count into the terminal, and displays the count in the status bar of the video. The second one uses openCV to draw the counter on the video frames.

The initial thought to counting, was to track the cars the for the entire travel past the camera, but that became soon very problematic due to the lack of robustness of the model when the cars aren't detected in every frame as they pass the camera. The solution to this was to count the cars passing through a single narrow vertical slice of the frame. The region of interest is drawn on the screen with a pink box. 
When a car enters the region, the center point of the detection is saved to a list. Next frame, the distance from current detections are measured against previous detections. If the distance calculated is less than a set distance temporary counter goes up by 1. When this counter goes down, the actual car counter gets incremented. This slightly filters the result, as detections lasting for only 1 frame do not get counted. 


This approach works as long as the car gets constantly detected through the roi. Sometimes, when the detection is not constant, a single car can count as multiple cars. Other sources of problems are cause by big cars and trucks and sometimes ordinary cars have multiple detection boxed overlapping. 






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