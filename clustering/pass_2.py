import os
import numpy as np
from common1 import *
from shot_sim import *
from PIL  import Image
video_name = '3wAQxJeyyXo'
video_folder_name = 'final_shots_' + video_name+'_buffer'
shot_genre_results = os.path.join(root_path,genre,shot_result_dir_name,video_folder_name)
pass_2 = os.path.join(root_path,genre,pass_2_shots_dir)
if not os.path.isdir(pass_2):
    os.mkdir(pass_2)
   
#from PIL import Image
#a = 'D:\YouTubeTop-vis\music_video\psy\seg_shot_bd'

#count = 0
#for file_name in os.listdir(a):
 #   file_path = os.path.join(a,file_name)
  #  b = Image.open(file_path)
  #  c = np.array(b)
  #  d = np.max(c)
  #  if d==0:
  #      print(count)

  #  count+=1
#storing features of major shots in dict
#feature_list = []
parent_shot_list =[]
shots_number = len(os.listdir(shot_genre_results))
for  i in range(shots_number):
    parent_shot_list.append(i)
feature_list = [None]*shots_number
initial_shots = sorted(os.listdir(shot_genre_results))
included_in_pass_2 = [False]*shots_number
#print(initial_shots)
#stop
for shot in initial_shots:
    print(shot)
    shot_dir_path = os.path.join(shot_genre_results,shot)
    shot_folder = sorted(os.listdir(shot_dir_path))
    #if len(shot_folder)>6:
    shot_head_path = os.path.join(shot_dir_path,shot_folder[0])
        #feature_dict[shot] =  get_embed(shot_head_path)
    #feature_list.append(get_embed(shot_head_path))
    #feature_list[int(shot)] = get_embed(shot_head_path)
    feature_list[int(shot)] = get_cluster_average_features(shot_dir_path)
#now looking at bottleneck shots
print("length of feature list is " + str(len(feature_list)) )
for shot in os.listdir(shot_genre_results):
    curr_shot_number = int(shot)
    shot_dir_path = os.path.join(shot_genre_results,shot)
    shot_folder = os.listdir(shot_dir_path)
    parent_shot = 'l'
    pass_2_sim = 0
    found  = False
    if len(shot_folder)<4:
        shot_head_path = os.path.join(shot_dir_path,shot_folder[0])
        # print(shot_head_path)
        shot_head_image_name = shot_folder[0]
        shot_head_image = Image.open(shot_head_path)
        for i in range(shots_number):
            curr_major_shot  = os.listdir(os.path.join(shot_genre_results,str(i)))
            #if  i!=curr_shot_number and len(curr_major_shot)>4:
            if  i!=curr_shot_number and included_in_pass_2[i]==False:
             print(i)
             print(curr_shot_number)
             curr_pass_2_sim = similarity_function_embed(feature_list[curr_shot_number],feature_list[i])
             
             if curr_pass_2_sim>pass_2_sim:
                 pass_2_sim = curr_pass_2_sim
                 parent_shot = str(i)
                 
                            
        if pass_2_sim>pass_2_sim_barrier:
            parent_shot_list[curr_shot_number] = parent_shot
            included_in_pass_2[curr_shot_number] =True
            #if not os.path.isdir(os.path.join(pass_2,parent_shot)):
             #   os.mkdir(os.path.join(pass_2,parent_shot))
            #new_shot_path = os.path.join(pass_2,parent_shot)
            #d = Image.open(shot_head_path)
            #d.save(os.path.join(new_shot_path,shot_head_image_name))
print(parent_shot_list)
for  i in range(shots_number):
    if parent_shot_list[i]!=i:
        folder_parent = os.path.join(shot_genre_results,parent_shot_list[i])
        if not os.path.isdir(folder_parent):
            folder_parent = os.path.join(shot_genre_results,parent_shot_list[int(parent_shot_list[i])])
        folder_child = os.path.join(shot_genre_results,str(i))
        folder_merge(folder_parent,folder_child)
        os.chdir(folder_child)
        for file_name in os.listdir(folder_child):
           file_path = os.path.join(folder_child,file_name) 
           try:
            os.remove(file_path)

           except OSError:
            print("deletion problem")    
        
        os.chdir(curr_dir)
        os.rmdir(folder_child)
        
        

      