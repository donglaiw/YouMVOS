import os
import glob
import subprocess
import json
from scipy.ndimage import zoom
from skimage.color import label2rgb, rgb2gray
import imageio
import numpy as np
import shutil

GENRE = {}
GENRE['animation'] = 'kid-animation'
GENRE['kid'] = 'kid-animation'
GENRE['cartoon'] = 'kid-animation'
GENRE['history'] = 'education'
GENRE['vlog'] = 'skit-show'
GENRE['comedy'] = 'skit-show'
GENRE['interview'] = 'skit-show'

## video-related function
def getVideoInfo(video_url):
    output_file = 'db/tmp.info'
    os.system('ffprobe %s > %s 2>&1' % (video_url, output_file))
    os_out = readtxt(output_file)
    info = [os_line for os_line in os_out if '[SAR 1:1' in os_line][0]
    info_s = info.split(',')
    sz = [x.strip().split(' ')[0] for x in info_s if '[SAR 1:1' in x][0]
    fps = [x.strip().split(' ')[0] for x in info_s if 'fps' in x][0]
    return sz, fps

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




def readtxt(filename):
    a= open(filename)
    content = a.readlines()
    a.close()
    return content

def mkdir(fn, opt = 'dir'):
    if opt == 'dir': 
        # Create the folder that the file is in.
        fn = os.path.dirname(fn)
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

def visSeg(img, seg, color = 0):
    clr = np.array(['black', 'blue', 'yellow', 'darkorange', 'magenta', 'cyan', 'yellowgreen', 'red', 'pink', 'indigo', 'green'])
    uid = np.unique(seg)
    ovrl_gray = 255.*label2rgb(seg, img, clr[uid[uid > 0]], bg_label = 0)
    if not color: return np.uint8(ovrl_gray)

    seg_mask = np.tile(seg[:, :, None] > 0, [1,1,3])
    seg_neg = np.tile(seg[:, :, None] == 0, [1,1,3])
    imx = np.zeros(img.shape)
    imx[seg_mask] = ovrl_gray[seg_mask]
    imx[seg_neg] = img[seg_neg]
    return np.uint8(imx)

def convertClusterStrToClusterList(cluster_str):
    if cluster_str[-1] == ';':
        cluster_str = cluster_str[:-1]
    cluster_list = [[int(y) for y in x.split(',')] for x in cluster_str.split(';')]
    return cluster_list


def convertClusterListToStr(shots):
    return ';'.join([','.join([str(y) for y in shots[x]]) for x in range(len(shots))]) 

def convertClusterArrToStr(cluster_ids):
    uid = np.unique(cluster_ids)
    return ';'.join([','.join([str(y) for y in np.where(cluster_ids==x)[0]]) for x in uid])


def convertClusterToJs(shots):
    if isinstance(shots, list):
        cluster_str = convertClusterListToStr(shots)
    elif isinstance(shots, numpy.ndarray):
        cluster_str = convertClusterArrToStr(shots)
    output_js = 'var shot_index_str="' + cluster_str + '";'
    output_js += 'var shot_selection_str="0";'
    return output_js

def copyFolder(input_folder, output_folder, file_ext='png', name_replace=[]):
    mkdir(output_folder)
    file_in = glob.glob(input_folder + '/*.' + file_ext)
    file_out = glob.glob(output_folder + '/*.' + file_ext)
    if len(file_in) == 0:
        print('no copy',input_folder,len(file_out),len(file_in))
    if len(file_in)>0 and len(file_out)!=len(file_in):
        for ff in file_in:
            file_name = ff[ff.rfind('/')+1:]
            if len(name_replace) != 0:
                file_name = file_name.replace(name_replace[0], name_replace[1])
            file_name = output_folder + file_name
            if not os.path.exists(file_name):
                shutil.copyfile(ff, file_name)
