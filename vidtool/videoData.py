import os
import shutil
import json
import imageio
import numpy as np

from . import videoUtil as vutil

class videoData(object):
    def __init__(self):
        pass
   
    def setProjectParam(self, project_txt):
        result = vutil.TxtToDict(project_txt, '=')
        for kk in result.keys():
            self.__dict__[kk] = result[kk]

    def getVideoFolder(self, video_url, video_genre=''):
        return 

    def getFrameFolder(self, video_folder, frame='frame/'):
        return os.path.join(video_folder, frame) 

    def getVideoFile(self, video_url, video_folder='./'):
        return os.path.join(video_folder, video_url+ '.mp4')

    def getFrameFile(self, frame_folder, frame_id = 0):
        return os.path.join(frame_folder, self.FRAME_FMT % frame_id)

    # define filenames for each video
    def setVideo(self, video_path):
        self.video_path = video_path
        self.video_url = video_path[video_path.rfind('/')+1:] if '/' in video_path else video_path

        self.video_folder = os.path.join(self.VIDEO_ROOT, video_path)
        self.video_file = os.path.join(self.video_folder, self.video_url+ '.mp4')
        self.frame_folder = os.path.join(self.video_folder, self.VIDEO_FRAME)
        self.frame_template = os.path.join(self.frame_folder, self.FRAME_FMT)
        self.frame_suffix = self.FRAME_FMT[self.FRAME_FMT.rfind('.')+1:]
        self.stats_folder = os.path.join(self.video_folder, self.VIDEO_STATS)

    # current video
    def setVideoInfo(self, video_path, frame_num = -1, frame_rate = -1):
        self.video_path = video_path
        self.video_genre = video_path[:video_path.rfind('/')]
        self.video_url = video_path[video_path.rfind('/')+1:]
        self.video_frame_num = frame_num
        self.video_frame_rate = frame_rate
        if self.video_all_info is not None:
            if frame_num < 0:
                self.video_frame_num = self.video_all_info[video_path]['num_frame']
            if frame_rate < 0:
                self.video_frame_rate = self.video_all_info[video_path]['fps']
            self.video_frame_size = self.video_all_info[video_path]['size']
            self.video_duration = self.video_all_info[video_path]['duration']
            self.video_frame_rate = int(np.round(self.video_frame_rate))
            
            # output 6fps
            if self.video_frame_rate in [25,30]:
                self.video_frame_step = 5
            elif self.video_frame_rate in [24]:
                self.video_frame_step = 4
            elif self.video_frame_rate in [27]:
                self.video_frame_step = 3
            else:
                raise ValueError('unknown frame rate %d' % self.video_frame_rate)


    ####
    # I/O for frames
    def getFrameImage(self, frame_id = 0, output_folder = None):
        return imageio.imread(self.getFrameName(frame_id, output_folder))

    def getFrameIndex(self, option = 'all', frame_rate = -1, frame_num = -1, input_file = None):
        # returninput can either be the input frame index
        # or the frame_index for the pre-defined frame index
        if option == 'uniform':
            # uniform N-frame
            frame_ids = np.linspace(0, self.video_frame_num - 1, frame_num).astype(int)
        else:
            if frame_rate < 0:
                frame_rate = self.video_frame_rate
                if '_out' in option:
                    frame_rate = self.video_frame_step
            frame_ids = np.arange(0, self.video_frame_num, frame_rate) + self.FRAME_OFFSET

            if 'shot' in option:
                if '_out' in option and input_file is None:
                    input_file = '_shot_out'
                # Js: natural index without the framerate info
                shots, shot_selection = self.loadShotJs(input_file, option='2d', frame_rate=frame_rate)
                if shots is None:
                    print('no shot label found')
                    return None
                shot_sel = 0
                if '_unclear' in option:
                    shot_sel = 2
                if 'shot_selected' in option: 
                    if '_min' in option:
                        # first frames in selected shots
                        # Exist single-frame shots
                        output_ids = frame_ids[np.unique(shots[shot_selection == shot_sel, 0])]
                    else: 
                        step = 1
                        if 'every' in option:
                            step = int(option[option.rfind('-')+1:])
                        # All frames in selected shots
                        output_ids = [None] * (shot_selection == shot_sel).sum()
                        for i, shot_id in enumerate(np.where(shot_selection == shot_sel)[0]):
                            tmp = list(frame_ids[range(shots[shot_id, 0], shots[shot_id, 1]+1)])
                            if step > 1:
                                tmp = list(np.unique(tmp[::step] + tmp[-1:]))
                            output_ids[i] = tmp
                            if len(tmp) == 0:
                                # check for labeling error
                                import pdb; pdb.set_trace()
                        if '_arr' in option: 
                            if len(output_ids) > 0:
                                output_ids = np.hstack(output_ids)
            elif 'cluster' in option:
                if input_file is None:
                    input_file = '_cluster'
                if '_out' in option:
                    input_file += '_out'
                cluster_ids = self.loadClusterJs(input_file, option)
                if isinstance(cluster_ids[0], list):
                    if '_arr' in option:
                        output_ids = np.hstack([frame_ids[x] for x in cluster_ids])
                    else:
                        output_ids = [frame_ids[x] for x in cluster_ids]
                else:
                    output_ids = frame_ids[cluster_ids]
            else:
                output_ids = frame_ids
        return output_ids

    ####
    # I/O for proofreading files
    def getTxt(self, txt_file = None, suf = ''):
        if txt_file is None:
            txt_file = self.FOLDER_DOWNLOAD.format(self.video_path)
        # input folder -> filename 
        if txt_file[-1] == '/':
            txt_file += suf + '.txt'
        return txt_file

    def getJs(self, suf = ''):
        if suf is None:
            suf = '_shot'
        return self.PROOFREADER_JS_SAVE % (self.video_genre, self.video_url, suf)

    def getHtml(self, suf = ''):
        return self.PROOFREADER_HTML_TEST % (self.video_genre, self.video_url, suf)

    def loadClusterJs(self, cluster_js = '_cluster', option = 'cluster'):
        cluster_js = self.getJs(cluster_js)
        cluster_info = vutil.readtxt(cluster_js)[0].strip()
        shot_ids = vutil.convertClusterStrToClusterList(cluster_info[cluster_info.find('=')+2:cluster_info.rfind('var')-2]) 
        if '_factor' in option:
            shot_ids = [list(np.array(x)*self.video_frame_rate+self.FRAME_OFFSET) for x in shot_ids]
        shot_selection = np.array([int(x) for x in cluster_info[cluster_info.rfind('=')+2:cluster_info.rfind('"')].split(',')]) 
        if option == 'cluster':
            return shot_ids, shot_selection
        if '_selected' in option:
            shot_ids = [shot_ids[x] for x in np.where(shot_selection == 0)[0]]
            if '_minA' in option:
                shot_ids = [sorted(x) for x in shot_ids]
            elif '_min' in option:
                shot_ids = [min(x) for x in shot_ids]
            elif '_midA' in option:
                shot_ids = [list(np.array(x)[np.argsort(x)[len(x)//2:]]) +\
                            list(np.array(x)[np.argsort(x)[len(x)//2-1::-1]]) for x in shot_ids]
            elif '_mid' in option:
                shot_ids = [x[np.argsort(x)[len(x)//2]] for x in shot_ids]
            elif '_maxA' in option:
                shot_ids = [sorted(x, reverse=True) for x in shot_ids]
            elif '_max' in option:
                shot_ids = [max(x) for x in shot_ids]
            elif '_every' in option:
                step = int(option[option.rfind('-')+1:])
                shot_ids = [np.unique(x[::step]+x[-1:]) for x in shot_ids]

        if '_str' in option:
            return vutil.convertClusterListToStr(shot_ids)
        elif '_arr' in option:
            return [j for i in shot_ids for j in i]
        else:
            return shot_ids

    def loadShotJs(self, shot_js='_shot', option = 0, frame_rate = -1):
        shot_js = self.getJs(shot_js)
        if not os.path.exists(shot_js):
            print(shot_js, 'non-existent')
            return None, None
        shot_info = vutil.readtxt(shot_js)[0].strip()
        # start frame (N)
        shots = np.array([int(x) for x in shot_info[shot_info.find('=')+2:shot_info.find(';')-1].split(',')])
        if option in ['2d', 2]:
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
