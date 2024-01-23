import os
import imageio
from glob import glob
import numpy as np

from . import videoUtil as vutil


class videoVisualizer(object):
    def __init__(self):
        self.redo = False

    def setRedo(self, redo):
        self.redo = redo

    def visClipGif(self, frame_folder = None, output_file = None, frame_stride = 1, frame_num = -1, frame_duration = 0.2, frame_type = 'video'):
        if frame_folder is None:
            frame_folder = self.data.getFrameName(-2, suffix = '_ds')
        if output_file is None:
            output_file = (self.data.PROOFREADER_GIF.format(self.data.video_name, frame_type))

        if not os.path.exists(output_file):
            vutil.mkdir(output_file, 'parent')
            frame_names = sorted(glob(frame_folder + '/*.png')) 

            if len(frame_names) == 0:
                print('No frames in %s' % (frame_folder))
                return
            if frame_num == -1:
                frame_names = frame_names[::frame_stride]
            else:
                frame_names = [frame_names[int(x)] for x in np.linspace(0, len(frame_names)-1, frame_num)]

            frame_size = list(imageio.imread(frame_names[0]).shape)
            output = np.zeros([len(frame_names)] + frame_size, np.uint8)
            for frame_id, frame_name in enumerate(frame_names):
                output[frame_id] = imageio.imread(frame_name)

            vutil.writegif(output_file, output, duration = frame_duration)


    def visShotGif(self, frame_downsample = 4, num_gif_frame = 5, frame_duration = 0.2):
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

    def visSegGif(self, frame_downsample = 4, frame_duration = 0.2, frame_alpha = 0.7):
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

    def visSegPng(self, image_template, mask_template, output_template, frame_ids, image_downsample = 1, mask_downsample = 1, mask_id_func = None):
        vutil.mkdir(output_template, 'parent')
        for frame_id in frame_ids:
            output_name = output_template % frame_id
            image_name = image_template % frame_id 
            if mask_id_func is None:
                mask_name = mask_template % frame_id 
            else:
                mask_name = mask_template % mask_id_func(frame_id) 
            if os.path.exists(mask_name) and (self.redo or not os.path.exists(output_name)):
                im = imageio.imread(image_name)[::image_downsample, ::image_downsample]
                seg = vutil.vast2Seg(imageio.imread(mask_name)[::mask_downsample, ::mask_downsample])
                """
                # hacky: fix image size
                if im.shape[0] == 2*seg.shape[0]:
                    im = im[::2, ::2]
                    imageio.imwrite(image_name, im) 
                if seg.shape[0] == 320:
                    imageio.imwrite(mask_name, imageio.imread(mask_name).transpose()) 
                    seg = seg.transpose()
                """

                try:
                    imageio.imwrite(output_name, vutil.visSeg(im, seg))
                except:
                    print(im.shape, seg.shape)
                    import pdb; pdb.set_trace()
