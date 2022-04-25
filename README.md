A Light-Weight Python Package for Video Processing
---


## Installation
```
pip install -r requirements.txt
pip install --editable .
```

## Tutorial: Annotate One YouTube Video
Put the YouTube video url and its category (optional) in a text file, e.g.,`data/video.txt`.
```
ozgcKw4MyvY,pet
7GV-pQ00PCs,cooking
G5frRzhSNJ8,howto
```

### A. Get video frames
- Download YouTube videos
```
python main.py download
```
- Extract frames
```
python main.py extract-frame
```
- Extract video info
```
python main.py extract-info
```

### B. Annotate frames at shot boundaries at 6 FPS
- Shot detection
```
python main.py shot-detection
```
- Shot detection
```
python main.py download -f data/video.txt
```




## Customized External Libraries
- [[youtube-dl]](https://youtube-dl.org/): video download
- [[FFmpeg]](https://www.ffmpeg.org/download.html): frame extraction
- [[Detectron2]](https://github.com/donglaiw/detectron2): 2D instance segmentation
- [[STM]](https://github.com/donglaiw/STM): object mask propagation 
