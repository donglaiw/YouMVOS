import os
import glob
import subprocess
import json
from scipy.ndimage import zoom
from skimage.color import label2rgb, rgb2gray
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

def visSeg(im, seg, option=0):
    alpha = 0.7
    if seg.ndim == 3:
        seg = seg[:,:,2]
    if option == 0: # gray image
        # to keep the color label consistent
        # make sure all indices are present
        # hack the first elements 
        seg_mid = seg.max()
        prev_val = seg[0,:seg_mid].copy()
        seg[0,:seg_mid] = range(seg_mid) 
        seg_color = label2rgb(seg, bg_label=0)
        seg_color[0,:seg_mid] = seg_color[0,prev_val]
        im_gray = rgb2gray(im)[:,:,None]
        output = (255*(alpha * im_gray + (1 - alpha) * seg_color)).astype(np.uint8)
        return output 
    elif option == 1: # original image
        out = im.copy()
        seg_colored = 255.*label2rgb(seg, colors = COLOR64)
        seg_mask = np.tile(seg[:, :, None]>0, [1,1,3])
        out[seg_mask] = (im[seg_mask].astype(float) * frame_alpha + seg_colored[seg_mask] * (1 - frame_alpha)).astype(np.uint8)
        return out
