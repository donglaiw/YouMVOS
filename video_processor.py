import os
import numpy as np
from glob import glob
from skimage.measure import label
from skimage.color import label2rgb
import imageio
from scipy.ndimage import zoom
import shutil

def writetxt(filename, content):
    a= open(filename,'w')
    if isinstance(content, (list,)):
        for ll in content:
            a.write(ll)
            if '\n' not in ll:
                a.write('\n')
    else:
        a.write(content)
    a.close()


def U_mkdir(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

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

class videoProcessor(object):
    def __init__(self, job_id = 0, job_num = 1, redo = False):
        self.job_id = job_id
        self.job_num = job_num
        self.redo = redo

    def setVideoInfo(self, output_folder, num_frame, fps, export_folder = None):
        self.output_folder = output_folder
        index_last = output_folder[:-1].rfind('/')
        index_second_last = output_folder[:index_last-1].rfind('/')
        self.genre_name = output_folder[index_second_last + 1 : index_last]
        self.video_name = output_folder[index_last + 1 : -1]
        self.num_frame = num_frame
        self.fps = int(np.round(fps))
        if export_folder is None:
            self.export_folder = self.output_folder + 'www/' 
        else:
            self.export_folder = export_folder + '%s/%s/' % (self.genre_name, self.video_name)
        U_mkdir(self.export_folder)

    def setRedo(self, redo):
        self.redo = redo

    def setGetFrameName(self, getFrameName):
        self.getFrameName = getFrameName

    def getFrame(self, frame_id):
        return imageio.imread(self.getFrameName(frame_id))

    def getFrameNameLocal(self, frame_id):
        name = self.getFrameName(frame_id)
        return name[name.rfind('/')+1:]

    def getStat(self, stat):
        stat_path = self.output_folder+'%s.txt'%stat
        if not os.path.exists(stat_path):
            raise ValueError('File does not exist: ', stat_path)
        return np.loadtxt(stat_path).astype(int)

    def processDownsample(self, frame_downsample = 4, frame_rate = -1):
        output_folder = self.export_folder+'frame_ds/'
        if frame_rate < 0 :
            frame_rate = self.fps
        if self.job_id == 0: # avoid multiple thread conflicts
            U_mkdir(output_folder)

        frame_size = np.array(self.getFrame(0).shape)
        frame_size[:2] = (frame_size[:2] + frame_downsample - 1) // frame_downsample
        frame_ids = np.arange(0, self.num_frame, frame_rate)
        for frame_id in frame_ids[self.job_id :: self.job_num]:
            output_file = output_folder + self.getFrameNameLocal(frame_id)
            if not os.path.exists(output_file):
                output = self.getFrame(frame_id)[::frame_downsample, ::frame_downsample]
                imageio.imwrite(output_file, output)

    def visualizeClip(self, frame_duration = 0.2):
        output_folder = self.export_folder
        output_file = output_folder + '%s_in.gif' % (self.video_name)
        if not os.path.exists(output_file):
            frame_names = sorted(glob(output_folder + 'frame_ds/*.png')) 
            if len(frame_names) == 0:
                raise ValueError('No frames in %s' % (output_folder + 'frame_ds/'))
            frame_size = list(imageio.imread(frame_names[0]).shape)
            output = np.zeros([len(frame_names)] + frame_size, np.uint8)
            for frame_id, frame_name in enumerate(frame_names):
                output[frame_id] = imageio.imread(frame_name)

            writegif(output_file, output, duration = frame_duration)

    def computeMaxDiff(self, frame_downsample=4):
        num_per_job = (self.num_frame + self.job_num - 1) // self.job_num
        
        if self.job_num != 1: # for long movies
            output_path_max = self.output_folder+'rgb_max/'
            output_path_diff = self.output_folder+'rgb_diff/'
            if self.job_id == 0: # avoid multiple thread conflicts
                U_mkdir(output_path_max)
                U_mkdir(output_path_diff)
            output_file_max = output_path_max + '%d_%d.txt'%(self.job_id, self.job_num)
            output_file_diff = output_path_diff + '%d_%d.txt'%(self.job_id, self.job_num)
        else: # for short videos
            output_file_max = self.output_folder+'rgb_max.txt'
            output_file_diff = self.output_folder+'rgb_diff.txt'

        do_max = not os.path.exists(output_file_max)
        do_diff = not os.path.exists(output_file_diff)
        if do_max or do_diff:
            # not using the last frame
            frame_range = range(self.job_id * num_per_job, min((self.job_id + 1) * num_per_job, self.num_frame-1))
            output_diff = np.zeros(len(frame_range), int)
            if frame_range[-1]==self.num_frame-2:
                output_max = np.zeros(len(frame_range)+1, int)
            else:
                output_max = np.zeros(len(frame_range), int)
            frame_current = self.getFrame(frame_range[0])[::frame_downsample, ::frame_downsample].astype(float)

            for i, frame_id in enumerate(frame_range):
                output_max[i] = frame_current.max()
                frame_next = self.getFrame(frame_id+1)[::frame_downsample, ::frame_downsample].astype(float)
                output_diff[i] = np.abs(frame_current - frame_next).mean()
                frame_current[:] = frame_next

            if frame_range[-1]==self.num_frame-2:
                output_max[-1] = frame_next.max()

            np.savetxt(output_file_max, output_max, '%d')
            np.savetxt(output_file_diff, output_diff, '%d')

    def computeMaxDiffCombine(self):
        for name in ['rgb_diff', 'rgb_max']:
            output_path = self.output_folder+name
            output_file = output_path+'.txt'
            if not os.path.exists(output_file):
                result_file = glob(output_path+'/*.txt')
                num_result = len(result_file)
                if num_result == 0:
                    raise ValueError('Empty Folder: ',output_path)
                else:
                    _, job_num = result_file[0][result_file[0].rfind('/')+1:result_file[0].find('.')].split('_')
                    job_num = int(job_num) 
                    if job_num != num_result:
                       raise ValueError('Missing %d Files'%(job_num-num_result))
                    else:
                        output_len = self.num_frame
                        if name == 'rgb_diff':
                            output_len = self.num_frame - 1
                        output = np.zeros(output_len, int)
                        start_id = 0
                        for job_id in range(job_num):
                            result = np.loadtxt(output_path+'/%d_%d.txt'%(job_id,job_num)).astype(int)
                            output[start_id:start_id+len(result)] = result
                            start_id += len(result)
                    np.savetxt(output_file, output, '%d')

    def computeShot(self, threshold_dark = 20, threshold_diff = 10, threshold_shot_len = 12):
        # ideal: 0s surround the peak
        # if not sure, connect things
        # also remove small shots
        
        if threshold_shot_len == 0:
            raise ValueError('threshold_shot_len must be bigger than 0')

        output_path = self.output_folder+'shot.txt'
        if not os.path.exists(output_path):
            rgb_max = self.getStat('rgb_max')
            rgb_diff = self.getStat('rgb_diff')
            
            # Break the video by dark frames.
            frame_chunk = label(rgb_max >= threshold_dark)
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
                if chunk_len[chunk_id + 1] > 2 * threshold_shot_len:
                    # Find initial change points by diff threshold
                    rgb_diff_chunk = rgb_diff[frame_id[0]:frame_id[-1]+1]
                    frame_change = np.where(rgb_diff_chunk[threshold_shot_len:-threshold_shot_len] >= threshold_diff)[0]+threshold_shot_len 

                    # Select change points with enough shot length (no other change points nearby)
                    frame_nearby = frame_change + np.arange(-threshold_shot_len, threshold_shot_len+1).reshape([-1,1])
                    frame_change_v2 = np.array([-1] \
                                   + list(frame_change[(rgb_diff_chunk[frame_nearby] >= threshold_diff).sum(axis=0)==1]) \
                                   + [len(rgb_diff_chunk)-1])

                    # remove dark frames
                    output[chunk_id] = frame_id[0]+np.vstack([frame_change_v2[:-1]+1, frame_change_v2[1:]]).T
                else:
                    output[chunk_id] = [frame_id[0], frame_id[-1]]
            
            np.savetxt(output_path, np.vstack(output), '%d')

    def proofreadShot(self, frame_rate = -1):
        if frame_rate < 0 :
            frame_rate = self.fps
        from template import template_proofread_shot
        output_shot_js = self.export_folder+'%s_shot.js' % (self.video_name)
        if self.redo or not os.path.exists(output_shot_js):
            shots = np.loadtxt(self.output_folder+'shot.txt').astype(int)
            # Take the ceil for the start frame.
            # Can be repeated due to overlap
            shots = np.unique((shots[:, 0] + frame_rate - 1) // frame_rate)
            output_var = 'var shot_start_str="'+','.join([str(x) for x in shots])+'";'
            output_var += 'var shot_selection_str="'+','.join([str(0) for x in shots])+'";'
            writetxt(output_shot_js, output_var)

        output_shot_html = self.export_folder+'%s_shot.html' % (self.video_name)
        if self.redo or not os.path.exists(output_shot_html):
            output = template_proofread_shot % (self.genre_name, self.video_name, (self.num_frame + self.fps) // self.fps, self.fps)
            writetxt(output_shot_html, output)
 
    def visualizeShot(self, frame_downsample = 4, num_gif_frame = 5, frame_duration = 0.2):
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

    def visualizeResult(self, frame_downsample = 4, frame_duration = 0.2, frame_alpha = 0.7):
        output_file = self.output_folder+'%s_o.gif' % (self.video_name)

        if not os.path.exists(output_file):
            result_frame_id = np.loadtxt(self.output_folder+'result/fid.txt').astype(int)
            result_files = sorted(glob(self.output_folder+'result/*.png'))
            assert len(result_frame_id) == len(result_files)
        
            frame_ids = np.arange(0, self.num_frame, self.fps)
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
                    # label2rgb(seg, image = im) option converts the image into gray
                    seg_colored = 255.*label2rgb(seg)
                    seg_mask = np.tile(seg[:, :, None]>0, [1,1,3])
                    im[seg_mask] = (im[seg_mask].astype(float) * frame_alpha + seg_colored[seg_mask] * (1 - frame_alpha)).astype(np.uint8)
                output[i] = im
            writegif(output_file, output, duration = frame_duration)

    def proofreadSeg(self, frame_rate = -1):
        # Output im.vsvi and seg.vsvi for VAST-lite proofreading
        if frame_rate < 0 :
            frame_rate = self.fps
        from template import template_proofread_seg
        frame_ids = np.arange(0, self.num_frame, self.fps)
        # output vsvi
        vsvi_type = ['im','seg']
        vsvi_filename = ['image_%05d.png','seg_%05d.png']
        for vsvi_id in range(len(vsvi_type)):
            output_vsvi = self.export_folder+'%s.vsvi' % (vsvi_type[vsvi_id])
            # ffmpeg starts from id=1
            frame_ids_str = ','.join([str(1 + x) for x in frame_ids])
            frame_size = np.array(self.getFrame(0).shape)
            if True:#not os.path.exists(output_vsvi):
                meta = "%s-%s %s" % (self.genre_name, self.video_name, vsvi_type[vsvi_id])
                image_template = r'.\%s\%s' % (vsvi_type[vsvi_id], vsvi_filename[vsvi_id])
                output = template_proofread_seg % (meta, image_template, 0, \
                                                   image_template, frame_size[1], frame_size[0], \
                                                   frame_ids_str, frame_size[1], frame_size[0], \
                                                   len(frame_ids), meta)
                writetxt(output_vsvi, output)
        # copy frames
        output_folder = self.export_folder+'im/'
        U_mkdir(output_folder)
        for frame_id in frame_ids:
            frame_name = self.getFrameName(frame_id)
            output_image = output_folder + frame_name[frame_name.rfind('/')+1:]
            if not os.path.exists(output_image):
                shutil.copy(frame_name, output_image)
