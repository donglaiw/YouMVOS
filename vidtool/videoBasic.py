import os
import shutil
import json
import imageio
import numpy as np
from . import videoUtil as vutil

class videoBasic(object):
    def __init__(self, job_id = 0, job_num = 1, redo = False):
        self.job_id = job_id
        self.job_num = job_num
        self.redo = redo

        self.video_all_info = None
        self.video_all_name = None
   
    ####
    # 0. I/O for computation config and video info
    def setSingleProcess(self):
        self.job_id = 0
        self.job_num = 1

    def setRedo(self, redo):
        self.redo = redo

    def setFolders(self, data_folder, web_folder = '', share_folder = ''):
        # data_folder: original mp4/frames
        # web_folder: web-based proofreading
        # share_folder: desktop-based proofreading
        self.data_folder = data_folder + '/'
        self.web_folder = web_folder + '/'
        self.share_folder = share_folder + '/'
    
    # all videos
    def setInputVideoTxt(self, input_file):
        vutil.checkVideoTxt(input_file)
        video_all_info = vutil.readtxt(input_file)
        self.video_all_name = [line.split(',')[0] for line in video_all_info]

    def setInputVideoJson(self, input_file):
        self.video_all_info = json.load(open(input_file))
        self.video_all_name = list(self.video_all_info.keys())

    # one video
    def setVideoInfo(self, video_name, frame_num = -1, frame_rate = -1):
        self.video_name = video_name
        self.video_genre = video_name[:video_name.rfind('/')]
        self.video_url = video_name[video_name.rfind('/')+1:]
        self.video_frame_num = frame_num
        self.video_frame_rate = frame_rate
        if self.video_all_info is not None:
            if frame_num < 0:
                self.video_frame_num = self.video_all_info[video_name]['num_frame']
            if frame_rate < 0:
                self.video_frame_rate = self.video_all_info[video_name]['fps']
            self.video_frame_size = self.video_all_info[video_name]['size']
        self.video_frame_rate = int(np.round(self.video_frame_rate))

        self.video_data_folder = self.data_folder + '/' + self.video_name + '/'
        self.video_web_folder = self.web_folder + '/%s/' + self.video_name + '/'
        self.video_share_folder = self.share_folder + '/%s/' + self.video_name + '/'

    ####
    # 1. I/O for all frames
    # 1.1 all frames
    def getFrameName(self, frame_id = 0, output_folder = None, suffix = ''):
        if output_folder is None:
            output_folder = self.video_data_folder + 'frame%s/' % suffix
        if frame_id == -2:
            return output_folder
        frame_name = output_folder + 'image_%05d.png'
        if frame_id >= 0:
            frame_name = frame_name % (frame_id+1)
        return frame_name 

    def getFrame(self, frame_id = 0, output_folder = None):
        return imageio.imread(self.getFrameName(frame_id, output_folder))

    def copyFrames(self, output_folder, frame_rate = -1, frame_downsample = 1):
        vutil.mkdir(output_folder)
        if frame_rate < 0:
            frame_rate = self.video_frame_rate

        frame_ids = np.arange(0, self.video_frame_num, self.video_frame_rate)
        for frame_id in frame_ids[self.job_id :: self.job_num]:
            frame_name_in = self.getFrameName(frame_id)
            frame_name_out = output_folder + frame_name_in[frame_name_in.rfind('/'):]
            if not os.path.exists(frame_name_out):
                if frame_downsample != 1:
                    output = imageio.imread(frame_name_in)[::frame_downsample, ::frame_downsample]
                    imageio.imwrite(frame_name_out, output)
                else:
                    shutil.copy(frame_name_in, frame_name_out)
    def processDownsample(self, output_folder = None, frame_downsample = 4, frame_rate = -1):
        if output_folder is None:
            output_folder = self.getFrameName(-2, suffix = '_ds')
        if frame_rate < 0 :
            frame_rate = self.video_frame_rate
        if self.job_id == 0: # avoid multiple thread conflicts
            vutil.mkdir(output_folder)

        frame_size = np.array(self.getFrame(0).shape)
        frame_size[:2] = (frame_size[:2] + frame_downsample - 1) // frame_downsample
        frame_ids = self.getKeyframeIndex()
        for frame_id in frame_ids[self.job_id :: self.job_num]:
            output_file = self.getFrameName(frame_id, output_folder)
            if not os.path.exists(output_file):
                output = self.getFrame(frame_id)[::frame_downsample, ::frame_downsample]
                imageio.imwrite(output_file, output)

    # 1.2 keyframes
    def getKeyframeSuf(self, option = 0):
        frame_suf = ''
        if isinstance(option, int):
            frame_suf = ['_all', '_shot_bd', '_shot'][option]
        return frame_suf


    def getKeyframeIndex(self, option = '', shot_folder = None, frame_rate = -1, frame_num = -1, frame_offset = 0):
        # returninput can either be the input frame index
        # or the frame_index for the pre-defined frame index
        if frame_num > -1 :
            # N-frame
            keyframes = np.linspace(0, self.video_frame_num - 1, frame_num).astype(int)
            return keyframes
        else:
            if frame_rate < 0:
                frame_rate = self.video_frame_rate
            # ffmpeg offset
            keyframes = np.arange(0, self.video_frame_num, frame_rate) + frame_offset

            if option == '':
                # All frames
                return keyframes
            elif option == 'para':
                # divided by job
                num_per_job = (len(keyframes) + self.job_num - 1) // self.job_num
                frame_range = range(self.job_id * num_per_job, min((self.job_id + 1) * num_per_job, len(keyframes)))
                return keyframes[frame_range]
            elif 'shot' in option:
                # Js: natural index without the framerate info
                shots, shot_selection = self.convertShotJsToArr(shot_folder, option=1)
                if option == 'shot': 
                    # first frames in selected shots
                    # Exist single-frame shots
                    frame_id = keyframes[np.unique(shots[shot_selection == 0, 0])]
                elif option == 'shot_all': 
                    # All frames in selected shots
                    frame_id = []
                    for shot_id in np.where(shot_selection == 0)[0]:
                        frame_id += list(keyframes[range(shots[shot_id, 0], shots[shot_id, 1]+1)])
                    frame_id = np.array(frame_id)
                elif option == 'shot_all_list': 
                    # All frames in selected shots
                    frame_id = [None] * (shot_selection == 0).sum()
                    for i, shot_id in enumerate(np.where(shot_selection == 0)[0]):
                        frame_id[i] = keyframes[range(shots[shot_id, 0], shots[shot_id, 1]+1)]
                return frame_id
    ####
    # 2. I/O for proofreading files
    def getTxt(self, txt_file = None, suf = ''):
        if txt_file is None:
            txt_file = self.video_data_folder
        # input folder -> filename 
        if txt_file[-1] == '/':
            txt_file += suf + '.txt'
        return txt_file

    def getJs(self, js_file = None, suf = ''):
        if js_file is None:
            js_file = (self.video_web_folder % 'proofread/')[:-1]
            js_file = js_file[:js_file.rfind('/')] + '/saved/'
        # input folder -> filename 
        if js_file[-1] == '/':
            js_file += '%s%s.js' % (self.video_url, suf)
        return js_file

    def getHtml(self, html_file = None, suf = ''):
        if html_file is None:
            html_file = (self.video_web_folder % 'proofread/')[:-1]
            html_file = html_file[:html_file.rfind('/')] + '/test/'
        # input folder -> filename 
        if html_file[-1] == '/':
            html_file += '%s%s.html' % (self.video_url, suf)
        return html_file

    def loadClusterJs(self, cluster_js, option = ''):
        cluster_js = self.getJs(cluster_js, '_cluster')
        cluster_info = vutil.readtxt(cluster_js)[0].strip()
        import pdb; pdb.set_trace()
        shot_index = vutil.convertClusterStrToClusterList(cluster_info[cluster_info.find('=')+2:cluster_info.rfind('var')-2]) 
        shot_selection = np.array([int(x) for x in cluster_info[cluster_info.rfind('=')+2:cluster_info.rfind('"')].split(',')]) 
        if option == '':
            return shot_index, shot_selection
        if 'selected_' in option:
            shot_index = [shot_index[x] for x in np.where(shot_selection == 0)[0]]
            if option == 'selected_list':
                return shot_index
            elif option == 'selected_str':
                return vutil.convertClusterListToStr(shot_index)


    def convertShotJsToArr(self, shot_js, option = 0, frame_rate = -1):
        shot_js = self.getJs(shot_js, '_shot')
        shot_info = vutil.readtxt(shot_js)[0].strip()
        # start frame (N)
        shots = np.array([int(x) for x in shot_info[shot_info.find('=')+2:shot_info.find(';')-1].split(',')]) 
        if option in [1, 2]:
            # start-end frame (N x 2)
            if frame_rate < 0:
                frame_rate = self.video_frame_rate
            frame_num = (self.video_frame_num + frame_rate - 1) // frame_rate 
            shots = np.vstack([shots, \
                               list(shots[1:] - 1) + [frame_num - 1]]).T
            if option == 2:
                # back to original index
                frame_ids = np.arange(0, self.video_frame_num, frame_rate)
                shots = frame_ids[shots]
                
        shot_selection = np.array([int(x) for x in shot_info[shot_info.rfind('=')+2:shot_info.rfind('"')].split(',')]) 

        return shots, shot_selection

    def convertShotArrToJs(self, shots, frame_rate = -1):
        # need consecutive numbers for easy editing
        if frame_rate < 0 :
            frame_rate = self.video_frame_rate

        # Take the ceil for the start frame.
        # Can be repeated due to frame_rate downsample
        if shots.ndim == 1:
            shots = [(shots[0] + frame_rate - 1) // frame_rate]
        else:
            shots = np.unique((shots[:, 0] + frame_rate - 1) // frame_rate)
        output_js = 'var shot_start_str="'+','.join([str(x) for x in shots])+'";'
        output_js += 'var shot_selection_str="'+','.join([str(0) for x in shots])+'";'
        return output_js


    ####
    # 3. visualization
    def visualizeClipGif(self, frame_folder = None, output_file = None, frame_stride = 1, frame_num = -1, frame_duration = 0.2):
        if frame_folder is None:
            frame_folder = self.getFrameName(-2, suffix = '_ds')
        if output_file is None:
            output_file = (self.video_web_folder % 'gif')[: -1] + '_video.gif'

        if not os.path.exists(output_file):
            vutil.mkdir(output_file, 1)
            frame_names = sorted(glob(frame_folder + '*.png')) 
            if frame_num == -1:
                frame_names = frame_names[::frame_stride]
            else:
                frame_names = [frame_names[int(x)] for x in np.linspace(0, len(frame_names)-1, frame_num)]

            if len(frame_names) == 0:
                raise ValueError('No frames in %s' % (frame_folder))
            frame_size = list(imageio.imread(frame_names[0]).shape)
            output = np.zeros([len(frame_names)] + frame_size, np.uint8)
            for frame_id, frame_name in enumerate(frame_names):
                output[frame_id] = imageio.imread(frame_name)

            vutil.writegif(output_file, output, duration = frame_duration)


    def visualizeShotGif(self, frame_downsample = 4, num_gif_frame = 5, frame_duration = 0.2):
        output_folder = self.export_folder+'shot/'
        if self.job_id == 0: # avoid multiple thread conflicts
            U_mkdir(output_folder)

        shot = self.getStat('shot')
        frame_size = np.array(self.getFrame(0).shape)
        frame_size[:2] = (frame_size[:2] + frame_downsample - 1) // frame_downsample
        output = np.zeros([num_gif_frame] + list(frame_size), np.uint8)
        for shot_id in range(self.job_id, shot.shape[0], self.job_num):
            output_file = output_folder + '%d.gif'%shot_id
            if not os.path.exists(output_file):
                try:
                    ll = np.linspace(shot[shot_id, 0], shot[shot_id, 1], num_gif_frame).astype(int)
                except:
                    import pdb; pdb.set_trace()
                for j in range(num_gif_frame):
                    output[j] = self.getFrame(ll[j])[::frame_downsample, ::frame_downsample]
                writegif(output_file, output, duration = frame_duration)

    def visualizeSegGif(self, frame_downsample = 4, frame_duration = 0.2, frame_alpha = 0.7):
        output_file = self.output_folder+'%s_o.gif' % (self.video_name)

        if not os.path.exists(output_file):
            result_frame_id = np.loadtxt(self.output_folder+'result/fid.txt').astype(int)
            result_files = sorted(glob(self.output_folder+'result/*.png'))
            assert len(result_frame_id) == len(result_files)
        
            frame_ids = np.arange(0, self.frame_num, self.fps)
            frame_size = np.array(self.getFrame(0).shape)
            frame_size[:2] = (frame_size[:2] + frame_downsample - 1) // frame_downsample
            output = np.zeros([len(frame_ids)] + list(frame_size), np.uint8)

            for i, frame_id in enumerate(frame_ids):
                im = self.getFrame(frame_id)[::frame_downsample, ::frame_downsample]
                if frame_id in result_frame_id:
                    seg_id = int(np.where(result_frame_id==frame_id)[0])
                    seg = imageio.imread(result_files[seg_id])[::frame_downsample, ::frame_downsample]
                    if seg.ndim == 3:
                        seg = seg[:,:,2]
                    im = vutil.visSeg(im, seg)
                output[i] = im
            writegif(output_file, output, duration = frame_duration)

    def visualizeSegPng(self, image_template=None, mask_template=None, output_template=None, output_prefix='refine_', frame_index=None, frame_downsample = 4):
        if image_template is None:
            image_template = (self.video_web_folder % 'frame_ds/') + 'image_%05d.png'
        if mask_template is None:
            mask_template = (self.video_share_folder % '') + 'seg_prop/seg_%05d.png'
        if output_template is None:
            output_template = (self.video_web_folder % 'seg_ds/') + output_prefix + '%05d.png'

        if isinstance(frame_index, str):
            if frame_index == 'shot_all':
                frame_index = self.getKeyframeIndex(frame_index)
        vutil.mkdir(output_template, 1)
        for frame_id in frame_index:
            output_name = output_template % (frame_id+1)
            mask_name = mask_template % (frame_id + 1)
            if os.path.exists(mask_name) and (self.redo or not os.path.exists(output_name)):
                im = self.getFrame(frame_id)[::frame_downsample, ::frame_downsample]
                seg = imageio.imread(mask_name)[::frame_downsample, ::frame_downsample]
                imageio.imwrite(output_name, vutil.visSeg(im, seg))
