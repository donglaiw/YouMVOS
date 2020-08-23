import os
import glob
import subprocess
import json
import imageio

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

    json.dump(output, open(output_js,'w'))


def downloadVideo(video_url, output_mp4 = None):
    if output_mp4 is None:
        output_mp4 = '%s.mp4' % (video_url) 
    if not os.path.exists(output_mp4):
        # 136: 1280x720
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
