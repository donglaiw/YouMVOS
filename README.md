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
- Extract frames (high-res for segmentation, low-res for visualization)
```
python main.py extract-frame
```
- Extract video info
```
python main.py extract-info
```

### B. Annotate selected frames at frame clusters at 6 FPS
- Downsample and cluster frames with CNN features
```
python main.py web-frame
python main.py cluster-frame
```
- Select cluster with actors to segment on the browser
```
python main.py web-setup
python main.py web-proofread-cluster
```
- Segment selected frames (based-on clusters) with Detectron2
```
python main.py detectron2-cluster
```
- Proofread segments for selected frames with VAST lite (use detection2 results
  as template to select actors)
```
python main.py detectron2-vast
```
- Manual correction and copy results to output folder
```
python main.py vast-copy-cluster
```

### C. Human-in-the-loop segment propagation at 6 FPS
- Propagate cluster center results to the first frames from shots within the cluster
```
python main.py STM-shot_first
```
- Manual correction and copy results to output folder
```
python main.py vast-copy-shot_first
```
- Propagate cluster center and shot results to every 10 frames from shots within the cluster
```
python main.py STM-shot_every10
```
- Manual correction and copy results to output folder
```
python main.py vast-copy-shot_every10
```
- Propagate cluster center/shot_first/every10 results to the rest frames
```
python main.py STM-shot_all
```
- Refine and copy seg results to release
```
python main.py release-seg-shot_all
```

### D. Shot-based error detection
- Shot detection
```
python main.py shot-detection
```
- Shot proofreading on the browser
```
python main.py web-proofread-shot 
```
- Segmentation proofreading on the browser
```
python main.py web-proofread-seg-release
```




## Customized External Libraries
- [[youtube-dl]](https://youtube-dl.org/): video download
- [[FFmpeg]](https://www.ffmpeg.org/download.html): frame extraction
- [[Detectron2]](https://github.com/donglaiw/detectron2): 2D instance segmentation
- [[STM]](https://github.com/donglaiw/STM): object mask propagation 
