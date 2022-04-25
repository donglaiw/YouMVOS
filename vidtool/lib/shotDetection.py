import numpy as np
import os
from glob import glob
from imageio import imread
from skimage.measure import label
from .. import videoUtil as vutil


class shotDetection(object):
    def __init__(self):
        pass

    # 1. Shot detection
    def setFolder(self, image_template, stat_folder):
        self.stat_folder = stat_folder
        self.image_template = image_template
        self.image_folder = os.path.dirname(image_template)
        self.image_suffix = image_template[image_template.rfind('.')+1:]

    def getStat(self, stat):
        stat_path = self.stat_folder + ('%s.txt'%stat)
        if not os.path.exists(stat_path):
            raise ValueError('File does not exist: ', stat_path)
        return np.loadtxt(stat_path).astype(int)

    def computeMaxDiff(self, job_id = 0, job_num = 1, frame_downsample=4):
        if job_num != 1: # for long movies
            output_path_max = os.path.join(self.stat_folder, 'rgb_max/')
            output_path_diff = os.path.join(self.stat_folder, 'rgb_diff/')
            if job_id == 0: # avoid multiple thread conflicts
                vutil.mkdir(output_path_max)
                vutil.mkdir(output_path_diff)
            output_file_max = os.path.join(output_path_max, '%d_%d.txt'%(job_id, job_num))
            output_file_diff = os.path.join(output_path_diff, '%d_%d.txt'%(job_id, job_num))
        else: # for short videos
            output_file_max = os.path.join(self.stat_folder, 'rgb_max.txt')
            output_file_diff = os.path.join(self.stat_folder, 'rgb_diff.txt')

        do_max = not os.path.exists(output_file_max)
        do_diff = not os.path.exists(output_file_diff)
        if do_max or do_diff:
            print('compute max/diff')

            frame_names = sorted(glob(os.path.join(self.image_folder, '*.'+self.image_suffix)))
            frame_num = len(frame_names)
            if frame_num == 0:
                raise ValueError('No images: %s' % self.image_template)
            # not using the last frame
            num_per_job = (frame_num + job_num - 1) // job_num
            # not using the last frame
            frame_range = range(job_id * num_per_job, min((job_id + 1) * num_per_job, frame_num)-1)
            frame_num_todo = len(frame_range)

            output_diff = np.zeros(frame_num_todo, int)
            # if last job
            if frame_range[-1] == frame_num-2:
                output_max = np.zeros(frame_num_todo + 1, int)
            else:
                output_max = np.zeros(frame_num_todo, int)
            frame_current = imread(frame_names[frame_range[0]])[::frame_downsample, ::frame_downsample].astype(float)

            for i, frame_id in enumerate(frame_range):
                output_max[i] = frame_current.max()
                frame_next = imread(frame_names[frame_id+1])[::frame_downsample, ::frame_downsample].astype(float)
                output_diff[i] = np.abs(frame_current - frame_next).mean()
                frame_current[:] = frame_next

            if frame_range[-1] == frame_num-2:
                output_max[-1] = frame_next.max()

            np.savetxt(output_file_diff, output_diff, '%d')
            np.savetxt(output_file_max, output_max, '%d')

    def computeMaxDiffCombine(self):
        for name in ['rgb_diff', 'rgb_max']:
            output_path = os.path.join(self.stat_folder, name)
            output_file = output_path+'.txt'
            if not os.path.exists(output_file):
                result_file = glob(os.path.join(output_path, '*.txt'))
                num_result = len(result_file)
                if num_result == 0:
                    raise ValueError('Empty Folder: ',output_path)
                else:
                    _, job_num = result_file[0][result_file[0].rfind('/')+1:result_file[0].find('.')].split('_')
                    job_num = int(job_num) 
                    if job_num != num_result:
                       raise ValueError('Missing %d Files'%(job_num-num_result))
                    else:
                        output_len = self.frame_num
                        if name == 'rgb_diff':
                            output_len = self.frame_num - 1
                        output = np.zeros(output_len, int)
                        start_id = 0
                        for job_id in range(job_num):
                            result = np.loadtxt(output_path+'/%d_%d.txt'%(job_id,job_num)).astype(int)
                            output[start_id:start_id+len(result)] = result
                            start_id += len(result)
                    np.savetxt(output_file, output, '%d')

    def computeShot(self, thres_dark = 20, thres_diff = 10, thres_shot_len = 12):
        # ideal: 0s surround the peak
        # if not sure, connect things
        # also remove small shots
        
        if thres_shot_len == 0:
            raise ValueError('thres_shot_len must be bigger than 0')

        output_file = os.path.join(self.stat_folder, 'shot.txt')
        if not os.path.exists(output_file):
            # if file not exist, combine separate files
            self.computeMaxDiffCombine()
            rgb_max = np.loadtxt(os.path.join(self.stat_folder, 'rgb_max.txt')).astype(int)
            rgb_diff = np.loadtxt(os.path.join(self.stat_folder, 'rgb_diff.txt')).astype(int)
            
            # Break the video by dark frames.
            frame_chunk = label(rgb_max >= thres_dark)
            _, chunk_len = np.unique(frame_chunk, return_counts = True)
            # If all 0s
            if len(chunk_len) == 1:
                chunk_len = np.hstack([0,chunk_len])
                frame_chunk[:] = 1 
            num_chunk = frame_chunk.max()
            output = [None]*num_chunk
            for chunk_id in range(num_chunk):
                frame_id = np.where(frame_chunk == chunk_id + 1)[0]
                print('%d: %d-%d' % (chunk_id, frame_id[0], frame_id[-1]))
                if chunk_len[chunk_id + 1] > 2 * thres_shot_len:
                    # Find initial change points by diff thres
                    rgb_diff_chunk = rgb_diff[frame_id[0]:frame_id[-1]+1]
                    frame_change = np.where(rgb_diff_chunk[thres_shot_len:-thres_shot_len] >= thres_diff)[0]+thres_shot_len 

                    # Select change points with enough shot length (no other change points nearby)
                    frame_nearby = frame_change + np.arange(-thres_shot_len, thres_shot_len+1).reshape([-1,1])
                    frame_change_v2 = np.array([-1] \
                                   + list(frame_change[(rgb_diff_chunk[frame_nearby] >= thres_diff).sum(axis=0)==1]) \
                                   + [len(rgb_diff_chunk)-1])

                    # remove dark frames
                    output[chunk_id] = frame_id[0]+np.vstack([frame_change_v2[:-1]+1, frame_change_v2[1:]]).T
                else:
                    output[chunk_id] = [frame_id[0], frame_id[-1]]
            np.savetxt(output_file, np.vstack(output), '%d')
