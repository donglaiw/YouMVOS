import os,glob
import shutil
import json
import imageio
import numpy as np

from . import videoUtil as vutil

class videoData(object):
    def __init__(self):
        self.videos_txt = None
        self.videos_info = None

    def setVideoList(self, videos_txt):
        if os.path.exists(videos_txt):
            self.videos_txt = videos_txt
            self.videos_name = [x[:-1].strip() for x in vutil.readtxt(videos_txt)]
        else:
            raise Exception('File not exist: %s' % videos_txt)

    def setVideoJson(self, videos_json=None):
        if videos_json is None:
            if len(self.videos_txt) != 0:
                videos_json = self.videos_txt.replace('.txt','.json')

        if not os.path.exists(videos_json):
            print("Need to 'extract-info' to get frame rate info")
            self.extractVideoInfo()
        self.videos_info = json.load(open(videos_json,'r'))

    def setProjectParam(self, project_txt):
        result = vutil.TxtToDict(project_txt, '=')
        for kk in result.keys():
            if result[kk].isnumeric():
                self.__dict__[kk] = int(result[kk])
            else: # for string, remove ""
                self.__dict__[kk] = result[kk].strip('"').strip("'")
        self.frame_suffix = self.FRAME_FMT[self.FRAME_FMT.rfind('.')+1:]
        self.web_proofread_folder = os.path.join(self.WEB_ROOT, self.WEB_PROOFREAD)
        self.web_proofread_folder_server = os.path.join(self.WEB_SERVER, self.WEB_PROOFREAD)

    def extractVideoInfo(self, videos_json=''):
        if self.videos_name is not None:
            if len(videos_json) == 0:
                videos_json = self.videos_txt.replace('.txt', '.json')
            output = {}
            for video_name in self.videos_name:
                self.setVideo(video_name)
                num_frame = len(glob.glob(os.path.join(self.video_frame_folder, '*.' + self.frame_suffix)))
                video_size, video_fps, video_duration = vutil.getVideoInfo(self.video_file)
                output[video_name] = {'url': self.video_url,
                                     'num_frame': num_frame,
                                     'fps': float(video_fps),
                                     'duration': video_duration,
                                      'size': [int(x) for x in video_size.split('x')][::-1]}
            json.dump(output, open(videos_json, 'w'))


    # define filenames for each video
    def setVideo(self, video_path):
        self.video_path = video_path
        self.video_url = video_path[video_path.rfind('/')+1:] if '/' in video_path else video_path
        self.video_genre = video_path[:video_path.rfind('/')] if '/' in video_path else '' 
        self.video_path_str =  video_path.replace('/','_').replace('\\','_')

        self.release_frame_template = os.path.join(self.RELEASE_ROOT, self.RELEASE_FRAME, self.video_path_str, self.RELEASE_FRAME_FMT)
        self.release_seg_template = os.path.join(self.RELEASE_ROOT, self.RELEASE_SEG, self.video_path_str, self.RELEASE_SEG_FMT)

        self.video_folder = os.path.join(self.VIDEO_ROOT, video_path)
        self.video_file = os.path.join(self.video_folder, self.video_url+ '.mp4')
        self.video_frame_folder = os.path.join(self.video_folder, self.VIDEO_FRAME)
        self.video_frame_template = os.path.join(self.video_frame_folder, self.FRAME_FMT)
        self.video_stats_folder = os.path.join(self.video_folder, self.VIDEO_STATS)
        self.video_stats_shot = os.path.join(self.video_stats_folder, 'shot.txt')
        self.video_stats_black = os.path.join(self.video_stats_folder, 'black_frame%d.txt' % self.FRAME_SAMPLE_NUM)
        self.video_stats_cluster = os.path.join(self.video_stats_folder, 'cluster.txt')
        
        self.web_folder = os.path.join(self.WEB_ROOT, '{}', video_path)
        self.web_folder_local = os.path.join('..', '..', '{}', video_path)
        self.web_frame_template = os.path.join(self.web_folder.format(self.WEB_FRAME), self.FRAME_FMT)
        self.web_frame_template_local = os.path.join(self.web_folder_local.format(self.WEB_FRAME), self.FRAME_FMT)
        self.web_proofread_file = os.path.join(self.web_proofread_folder, video_path)
        self.web_proofread_cluster = self.web_proofread_file + '_cluster.js'
        self.web_proofread_shot = self.web_proofread_file + '_shot.js'
        self.web_proofread_server = self.web_proofread_folder_server + '/'+ video_path + '_{}.html'

        self.web_proofread_seg = os.path.join(self.web_folder.format(self.WEB_SEG), '{}_'+self.SEG_FMT)
        self.web_proofread_seg_local = os.path.join(self.web_folder_local.format(self.WEB_SEG), '{}_'+self.SEG_FMT)

        self.vast_folder = os.path.join(self.VAST_ROOT, video_path)
        self.vast_frame_template = os.path.join(self.vast_folder, self.VAST_FRAME, self.FRAME_FMT)
        self.vast_detectron2 = os.path.join(self.vast_folder, self.VAST_DETECTRON2)
        self.vast_cluster = os.path.join(self.vast_folder, self.VAST_CLUSTER)
        self.vast_stm = os.path.join(self.vast_folder, self.VAST_STM)
        self.vast_stm_release = os.path.join(self.vast_folder, self.VAST_STM.format('_out'))

        if self.videos_info is not None:
            self.frame_num = self.videos_info[video_path]['num_frame']
            self.frame_rate = int(np.round(self.videos_info[video_path]['fps']))
            self.frame_size = self.videos_info[video_path]['size']
            self.video_duration = self.videos_info[video_path]['duration']
            # frame sampling to output approximate 6-fps video
            if self.frame_rate in [25,30]:
                self.frame_step = 5
            elif self.frame_rate in [24]:
                self.frame_step = 4
            elif self.frame_rate in [27]:
                self.frame_step = 3
            else:
                raise ValueError('unknown frame rate %d' % self.frame_rate)


    ####
    # I/O for frames
    def getFrameImage(self, frame_id = 0, output_folder = None):
        return imageio.imread(self.getFrameName(frame_id, output_folder))

    def getFrameIndex(self, option = 'all', frame_rate = -1, input_file = None):
        # returninput can either be the input frame index
        # or the frame_index for the pre-defined frame index
        if 'uniform' in option:
            # uniform N-frame
            N = int(option[7:])
            output_ids = np.linspace(0, self.frame_num - 1, N).astype(int)
        else:
            if frame_rate < 0:
                # default 6 FPS
                frame_rate = self.frame_step
            frame_ids = np.arange(0, self.frame_num, frame_rate) + self.FRAME_OFFSET
            if option == '1fps':
                output_ids = frame_ids[::self.frame_step]
            elif 'cluster' in option:
                cluster_ids = self.loadClusterJs(input_file, option)
                if isinstance(cluster_ids[0], list):
                    if '_arr' in option:
                        output_ids = np.hstack([frame_ids[x] for x in cluster_ids])
                    else:
                        output_ids = [frame_ids[x] for x in cluster_ids]
                else:
                    output_ids = frame_ids[cluster_ids]
            elif 'shot' in option:
                if input_file is None:
                    input_file = '_shot'
                    if '_out' in option:
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
                            step = int(option[option.rfind('every')+5:])
                        # All frames in selected shots
                        if '1fps' in option:
                            frame_1fps = frame_ids[::self.frame_step]
                        output_ids = [None] * (shot_selection == shot_sel).sum()
                        for i, shot_id in enumerate(np.where(shot_selection == shot_sel)[0]):
                            tmp = list(frame_ids[range(shots[shot_id, 0], shots[shot_id, 1]+1)])
                            if step > 1:
                                tmp = list(np.unique(tmp[::step] + tmp[-1:]))
                            if '1fps' in option:
                                tmp = vutil.removeArr(tmp, frame_1fps, False)
                            if len(tmp) == 0:
                                # check for labeling error
                                import pdb; pdb.set_trace()
                            output_ids[i] = tmp
                        if '_arr' in option: 
                            if len(output_ids) > 0:
                                output_ids = np.hstack(output_ids)
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

    def getHtml(self, suf = ''):
        return self.PROOFREADER_HTML_TEST % (self.video_genre, self.video_url, suf)

    def loadClusterJs(self, input_file, option = 'cluster'):
        cluster_info = vutil.readtxt(input_file)[0].strip()
        shot_ids = vutil.convertClusterStrToClusterList(cluster_info[cluster_info.find('=')+2:cluster_info.rfind('var')-2]) 
        if '_factor' in option:
            shot_ids = [list(np.array(x)*self.frame_rate+self.FRAME_OFFSET) for x in shot_ids]
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
            elif '_all' in option:
                pass
            elif '_shot' in option:
                # sort frames in the cluster
                out = [None] * len(shot_ids)
                for sid, shots in enumerate(shot_ids):
                    tmp = np.array(sorted(shots))
                    tmp_dif = tmp[1:] - tmp[:-1]
                    tmp_pos = np.where(tmp_dif!=1)[0]
                    if '_first' in option:
                        out[sid] = np.hstack([[0], tmp_pos+1])
                    elif '_last' in option:
                        out[sid] = np.hstack([tmp_pos+1, len(tmp)-1])
                    elif '_every' in option:# every10
                        step = int(option[option.rfind('every')+5:])
                        out[sid] = []
                        if len(tmp_pos) == 0:
                            if len(tmp) > step:
                                out[sid] = np.arange(len(tmp))[::step]
                        else:
                            if tmp_pos[0] > step:
                                out[sid].append(np.arange(tmp_pos[0]+1)[::step])
                            if len(tmp) - tmp_pos[-1] - 1 > step:
                                out[sid].append(np.arange(tmp_pos[-1]+1, len(tmp))[::step])
                            shot_len = tmp_pos[1:] - tmp_pos[:-1]
                            for x in np.where(shot_len > step)[0]:
                                out[sid].append(np.arange(tmp_pos[x]+1, tmp_pos[x+1]+1)[::step])
                            if len(out[sid]) > 0:
                                out[sid] = np.hstack(out[sid])
                    #out[sid] = list(tmp[out[sid]]*self.frame_step+self.FRAME_OFFSET)
                    out[sid] = list(tmp[out[sid]])
                #shot_ids = [x for xs in out for x in xs]
                shot_ids = out
            elif '_first' in option:
                shot_ids = [x[0] for x in shot_ids]
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
        shot_js = self.web_proofread_file + shot_js +'.js'
        if not os.path.exists(shot_js):
            print(shot_js, 'non-existent')
            return None, None
        shot_info = vutil.readtxt(shot_js)[0].strip()
        # start frame (N)
        shots = np.array([int(x) for x in shot_info[shot_info.find('=')+2:shot_info.find(';')-1].split(',')])
        if option in ['2d', 2]:
            # start-end frame (N x 2)
            if frame_rate < 0:
                frame_rate = self.frame_rate
            frame_num = (self.frame_num + frame_rate - 1) // frame_rate 
            shots = np.vstack([shots, \
                               list(shots[1:] - 1) + [frame_num - 1]]).T
            if option == 2:
                # back to original index
                frame_ids = np.arange(0, self.frame_num, frame_rate)
                shots = frame_ids[shots]
        shot_selection = np.array([int(x) for x in shot_info[shot_info.rfind('=')+2:shot_info.rfind('"')].split(',')]) 
        return shots, shot_selection

    def getSTMIndex(self, cluster_file, option_inputs, option_output):
        if isinstance(option_inputs[0], str): 
            for i, option_input in enumerate(option_inputs):
                tmp = self.getFrameIndex(option_input, input_file=cluster_file)
                if isinstance(tmp[0], int) or isinstance(tmp[0], np.int64):
                    if 'fps' in option_input:
                        tmp2 = self.getFrameIndex('cluster_selected_all', input_file=cluster_file)
                        tmp = [vutil.removeArr(tmp,x,False) for x in tmp2]
                    else:
                        tmp = [[x] for x in tmp]

                if i == 0:
                    input_image_index = tmp
                else:
                    input_image_index = [list(np.unique(np.hstack([x,y]))) for x, y in zip(input_image_index, tmp)]
        else: # directly input index
            input_image_index = option_inputs

        if isinstance(option_output, str): 
            output_image_index = self.getFrameIndex(option_output, input_file=cluster_file)
            output_image_index = [vutil.removeArr(output_image_index[x], input_image_index[x]) for x in range(len(output_image_index))]

        else:
            output_image_index = option_output
            input_image_index = [vutil.removeArr(input_image_index, x, False) for x in output_image_index]
            output_image_index = [vutil.removeArr(y, x) for x,y in zip(input_image_index,output_image_index)]
        # both array need to be non-empty
        gid = [min(len(x),len(y)) for x,y in zip(input_image_index,output_image_index)]
        input_image_index = [y for x,y in zip(gid, input_image_index) if x>0]
        output_image_index = [y for x,y in zip(gid, output_image_index) if x>0]

        output_mask_index = [None]*len(output_image_index)
        first_id = 0
        for x in range(len(output_image_index)):
            last_id = first_id + len(output_image_index[x])
            output_mask_index[x] = range(first_id, last_id)
            first_id = last_id

        return input_image_index, output_image_index, output_mask_index
