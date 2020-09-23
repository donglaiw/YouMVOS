import os
#root_path = 'D:/YouTubeTop-vis/cooking/3nUKwvFsjA4'
#shots_dir = 'D:/YouTubeTop-vis/cooking/3nUKwvFsjA4/final_shots'
from common1 import *

def generate_txt_file(video_name):
 results_dir_path = os.path.join(root_path,'result_txt_files'+'_'+genre)
 if not os.path.isdir(results_dir_path):
    os.mkdir(results_dir_path)

 shots_dir = os.path.join(root_path,genre,shot_result_dir_name,'final_shots'+'_'+video_name)
 txt_file_dir = os.path.join(results_dir_path,video_name)
 if not os.path.isdir(txt_file_dir):
     os.mkdir(txt_file_dir)
 
 txt_file_path = os.path.join(txt_file_dir,'info.txt')
 txt_file = open(txt_file_path,'w')
 list1 = sorted(os.listdir(shots_dir))
 total_count = len(list1)
 #curr_max = 0
 for shot_name in range(total_count):
    shot_dir = os.path.join(shots_dir,str(shot_name))
    #print(shot_dir)
    #print(shot_dir)
    count = 0
    for file_name in sorted(os.listdir(shot_dir)):
        word1 = file_name.split()
        #print(word1)
        if count>0:
         txt_file.write(',')
        count+=1 
        started = False
        for word in list(file_name):
            print(word)
            #print('1')
            if word.isdigit():
                print('h')
                if int(word)>0 or started == True:
                    started  = True
                    print('y')
                    txt_file.write(word)
        
    #txt_file.seek(-1, os.SEEK_END)
    #txt_file.truncate() 
    #txt_file.write('shot_1_complete')   
    txt_file.write(';')                
