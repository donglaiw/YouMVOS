import os
import subprocess
import imageio

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

def writetxt(filename, content):
    a= open(filename,'w')
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
