import os
import glob
import subprocess
import json
from scipy.ndimage import zoom
import imageio
import numpy as np

GENRE = {}
GENRE['animation'] = 'kid-animation'
GENRE['kid'] = 'kid-animation'
GENRE['cartoon'] = 'kid-animation'
GENRE['history'] = 'education'
GENRE['vlog'] = 'skit-show'
GENRE['comedy'] = 'skit-show'
GENRE['interview'] = 'skit-show'


def getVideoInfo(video_url):
    output_file = 'db/tmp.info'
    os.system('ffprobe %s > %s 2>&1' % (video_url, output_file))
    os_out = readtxt(output_file)
    info = [os_line for os_line in os_out if '[SAR 1:1' in os_line][0]
    info_s = info.split(',')
    sz = [x.strip().split(' ')[0] for x in info_s if '[SAR 1:1' in x][0]
    fps = [x.strip().split(' ')[0] for x in info_s if 'fps' in x][0]
    return sz, fps

def VideoTxtToJson(input_txt, output_json, video_folder, frame_folder):
    input_videos = readtxt(input_txt)
    output = {}
    for line in input_videos:
        video_name, video_author, video_title = line[:-1].split(',')
        video_url = video_name[video_name.rfind('/') + 1 : ]
        num_frame = len(glob.glob(frame_folder + video_name + '/frame/*.png'))
        video_size, video_fps = getVideoInfo(video_folder + video_name + '/' + video_url + '.mp4')
        output[video_name] = {'author': video_author,
                             'title': video_title,
                             'num_frame': num_frame,
                             'fps': float(video_fps),
                             'size': [int(x) for x in video_size.split('x')]}
    json.dump(output, open(output_json,'w'))

def VideoTxtToJs(input_txt, output_js):
    input_videos = readtxt(input_txt)
    video_names = ['"' + x.split(',')[0] + '"' for x in input_videos]
    output = 'var video_name = [' + ','.join(video_names) + '];'

    writetxt(output_js, output)


def downloadVideo(video_url, output_mp4 = None):
    if output_mp4 is None:
        output_mp4 = '%s.mp4' % (video_url) 
    if not os.path.exists(output_mp4):
        # 136: 1280x720
        if video_url[0] == '-':
            output_mp4 = '-- ' + output_mp4
            video_url = '-- ' + video_url
        cmd = "youtube-dl --no-check-certificate -f 136 " + video_url + " -o " + output_mp4
        print(cmd)
        mkdir(output_mp4, 1)
        os.system(cmd)

def checkVideoSize(input_mp4, desired_size = '1280x'):
    if os.path.exists(input_mp4):
        sz, _ = getVideoInfo(input_mp4)
        if desired_size not in sz:
            print(input_mp4, sz)
    else:
        print(input_mp4, "Doesn't exist.")

def checkVideoTxt(input_file):
    # genre/video_url, author, title 
    videos = readtxt(input_file)
    for line in videos:
        tmp = line.split(',')
        if len(tmp) != 3:
            print("each line should be: genre/video_url, author, title") 
            raise ValueError('Wrong input format: ', line)


def readtxt(filename):
    a= open(filename)
    content = a.readlines()
    a.close()
    return content

def mkdir(fn, opt = 0):
    if opt == 1: 
        # Create the folder that the file is in.
        fn = fn[:fn.rfind('/')]
    if not os.path.exists(fn):
        os.makedirs(fn)

def writetxt(filename, content, mode='w'):
    a= open(filename, mode)
    if isinstance(content, (list,)):
        for ll in content:
            if '\n' not in ll:
                ll += '\n'
            a.write(ll)
    else:
        a.write(content)
    a.close()

def writegif(outname, vol, ratio=1, duration=0.5):
    if not isinstance(vol, list):# vol -> list
        out = [None]*vol.shape[0]
        for cc in range(vol.shape[0]):
            if ratio == 1:
                out[cc] = vol[cc]
            else:
                out[cc] = zoom(vol[cc], ratio, order=1)
    else:
        if ratio != 1:
            for cc in range(len(vol)):
                vol[cc] = zoom(vol[cc], ratio, order=1)
        out = vol
    imageio.mimsave(outname, out, 'GIF', duration=duration)

def segRefineGrabcut(im, seg, iter_image = 30, iter_algo = 50): 
    from scipy.ndimage.morphology import binary_erosion, binary_dilation
    from scipy.ndimage.morphology import distance_transform_edt
    import cv2
    
    seg_new = None
    if seg.max() > 0:
        sz = im.shape
        uid = np.unique(seg)
        uid = uid[uid>0]

        bgdModel = np.zeros((1,65),np.float64)
        fgdModel = np.zeros((1,65),np.float64)
        
        mask = np.zeros(sz[:2], np.uint8)
        seg_new = np.zeros(sz[:2], seg.dtype)
        for i in uid:
            mask[:] = 0
            mask_in = binary_erosion(seg == i, iterations = iter_image)
            mask[mask_in > 0] = 1
            mask_in = binary_dilation(seg == i, iterations = iter_image)
            mask[(mask_in > 0) * (mask == 0)] = 3

            dist = distance_transform_edt(seg != i)
            mask[(dist < iter_image * 2) * (mask == 0)] = 2

            out, bgdModel, fgdModel = cv2.grabCut(im, mask, None, bgdModel, fgdModel, iter_algo, cv2.GC_INIT_WITH_MASK)
            out2 = np.where((out == cv2.GC_BGD) | (out == cv2.GC_PR_BGD), 0, 1)
            seg_new[out2 > 0] = i
    return seg_new

def convertClusterStrToClusterList(cluster_str):
    if cluster_str[-1] == ';':
        cluster_str = cluster_str[:-1]
    cluster_list = [[int(y) for y in x.split(',')] for x in cluster_str.split(';')]
    return cluster_list

def convertClusterListToStr(shots):
    return ';'.join([','.join([str(y) for y in shots[x]]) for x in range(len(shots))]) 

def convertClusterListToJs(shots):
    cluster_str = convertClusterListToStr(shots)
    output_js = 'var shot_index_str="' + cluster_str + '";'
    output_js += 'var shot_selection_str="0";'
    return output_js

def copyFolder(input_folder, output_folder, file_ext='png'):
    mkdir(output_folder)
    file_in = glob.glob(input_folder + '/*.' + file_ext)
    file_out = glob.glob(output_folder + '/*.' + file_ext)
    if len(file_in)>0 and len(file_out)!=len(file_in):
        print('copy')
        for ff in file_in:
            file_name = ff[ff.rfind('/')+1:]
            if not os.path.exists(output_folder + file_name):
                shutil.copyfile(ff, output_folder + file_name)
