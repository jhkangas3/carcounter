# Computer Vision car counter

This program will count the amount of cars passing the camera.

![](my_video2.mp4)





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
