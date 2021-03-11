import os
import glob
import subprocess
import json
from scipy.ndimage import zoom
from skimage.color import label2rgb, rgb2gray
import imageio
import numpy as np
import shutil
from data import secret

def vast2Seg(seg):
    # can't be more than 255 objects...
    if seg.ndim==2:
        return seg 
    else:
        return seg[:,:,2]

## video-related function
def getVideoInfo(video_url):
    output_file = 'db/tmp.info'
    os.system('ffprobe %s > %s 2>&1' % (video_url, output_file))
    os_out = readtxt(output_file)
    info = [os_line for os_line in os_out if '[SAR 1:1' in os_line][0]
    info_s = info.split(',')
    sz = [x.strip().split(' ')[0] for x in info_s if '[SAR 1:1' in x][0]
    fps = [x.strip().split(' ')[0] for x in info_s if 'fps' in x][0]

    info = [os_line for os_line in os_out if 'Duration:' in os_line][0]
    info_s = [float(x) for x in info[info.find(':')+1:info.find(',')].split(':')]
    duration = (np.array([3600,60,1])*info_s).sum()
    return sz, fps, duration


def downloadVideo(video_url, output_mp4 = None, option=136):
    if output_mp4 is None:
        output_mp4 = '%s.mp4' % (video_url) 
    if not os.path.exists(output_mp4):
        # 136: 1280x720
        if video_url[0] == '-':
            #output_mp4 = '-- ' + output_mp4
            video_url = 'https://www.youtube.com/watch?v=' + video_url
        cmd = "youtube-dl --no-check-certificate -f %d "%option + video_url + " -o " + output_mp4
        print(cmd)
        mkdir(output_mp4, 'dir')
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
        video_size, video_fps, video_duration = getVideoInfo(video_folder + video_name + '/' + video_url + '.mp4')
        output[video_name] = {'author': video_author,
                             'title': video_title,
                             'num_frame': num_frame,
                             'fps': float(video_fps),
                             'duration': video_duration,
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

def remove(fn, opt = ''):
    if os.path.exists(fn):
        if opt =='':
            os.remove(fn)
        else:
            shutil.rmtree(fn)
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
    ovrl_gray = 255.*label2rgb(seg, img, clr[uid[uid > 0] % (len(clr))], bg_label = 0)
    if not color: return np.uint8(ovrl_gray)

    seg_mask = np.tile(seg[:, :, None] > 0, [1,1,3])
    seg_neg = np.tile(seg[:, :, None] == 0, [1,1,3])
    imx = np.zeros(img.shape)
    imx[seg_mask] = ovrl_gray[seg_mask]
    imx[seg_neg] = img[seg_neg]
    return np.uint8(imx)

def converListToJsArr(in_list):
    out = '['
    for ll in in_list:
        out += '[' + ll[:-1] + '],'
    out = out[:-1] + '];'
    return out

def converArrToStr(in_arr):
    return ','.join([str(x) for x in in_arr])

def convertClusterStrToClusterList(cluster_str):
    if cluster_str[-1] == ';':
        cluster_str = cluster_str[:-1]
    cluster_str_list = cluster_str.split(';')
    cluster_list = [None] * len(cluster_str_list)
    for i,x in enumerate(cluster_str_list):
        out = []
        for y in x.split(','):
            if '-' in y:
                tmp = [int(z) for z in y.split('-')]
                out += range(tmp[0], tmp[1]+1)
            else:
                out += [int(y)]
        cluster_list[i] = out
    return cluster_list

def convertClusterListToStr(shots):
    return ';'.join([','.join([str(y) for y in shots[x]]) for x in range(len(shots))]) + ';'

def convertClusterArrToStr(cluster_ids):
    uid = np.unique(cluster_ids)
    return ';'.join([','.join([str(y) for y in np.where(cluster_ids==x)[0]]) for x in uid]) + ';'

def convertClusterListToShot(clusters, clusters_sel, frame_rate=1):
    shots = []
    shots_sel = []
    for cid, cluster in enumerate(clusters):
        cluster = sorted(cluster)
        lt = [x for x in range(1,len(cluster)) if cluster[x]-cluster[x-1]!=frame_rate]
        if len(cluster) == 1 or len(lt)==0:
            shots += [[cluster[0], cluster[-1]]]
            shots_sel += [clusters_sel[cid]]
        else:
            st = [0] + lt[:-1]
            tmp = [[cluster[st[x]],cluster[lt[x]-1]] for x in range(len(st))]
            tmp += [[cluster[lt[-1]], cluster[-1]]]
            shots += tmp
            shots_sel += [clusters_sel[cid]] * len(tmp)
    # sorted
    shots = np.vstack(shots)
    sid = np.argsort(shots[:,0])
    return shots[sid], np.array(shots_sel)[sid]

def convertClusterToJs(shots):
    if isinstance(shots, list):
        num_shots = len(shots)
        cluster_str = convertClusterListToStr(shots)
    elif isinstance(shots, np.ndarray):
        cluster_str = convertClusterArrToStr(shots)
        num_shots = shots.max()
    output_js = 'var shot_index_str="' + cluster_str + '";'
    output_js += 'var shot_selection_str="' + ','.join('0'*num_shots) + '";'
    return output_js

def convertShotToJs(shots, shots_sel = None, frame_rate = 1):
    # need consecutive numbers for easy editing
    # Take the ceil for the start frame.
    # Can be repeated due to frame_rate downsample
    if shots.ndim == 1:
        shots = (shots + frame_rate - 1) // frame_rate
    else:
        shots = np.unique((shots[:, 0] + frame_rate - 1) // frame_rate)
    output_js = 'var shot_start_str="'+','.join([str(x) for x in shots])+'";'
    if shots_sel is None:
        shots_sel = np.zeros(len(shots), int) 
    output_js += 'var shot_selection_str="'+','.join([str(x) for x in shots_sel])+'";'
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

def getVideoViews(video_url):
    tmp_file = 'db/views/v%s.json' % video_url
    if not os.path.exists(tmp_file):
        os.system('wget "https://www.googleapis.com/youtube/v3/videos?part=statistics&id=%s&key=%s" -O %s' %(video_url, secret.YOUTUBE_API_KEY, tmp_file))
    data = json.load(open(tmp_file))
    if len(data['items']) >0 and 'statistics' in data['items'][0]:
        return int(data['items'][0]['statistics']['viewCount'])
    else:
        return -1

def getVideoFrameStep(fps):
    if fps in [25,30]:
        fps = 5
    elif fps in [24]:
        fps = 4
    elif fps in [27]:
        fps = 3
    return fps

