import os
from common1 import *
import txt_file_write
import shot_sim
root_genre_path = os.path.join(root_path,genre)
for video_name in os.listdir(root_genre_path):
    shot_sim.run_shot_sim(video_name)
    txt_file_write.generate_txt_file(video_name)