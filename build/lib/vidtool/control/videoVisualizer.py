import os
import imageio

from .. import videoUtil as vutil


class videoVisualizer(object):
    def __init__(self, data = None):
        self.data = data

    def visClipGif(self, frame_folder = None, output_file = None, frame_stride = 1, frame_num = -1, frame_duration = 0.2):
        if frame_folder is None:
            frame_folder = self.getFrameName(-2, suffix = '_ds')
        if output_file is None:
            output_file = (self.video_folder_web % 'gif')[: -1] + '_video.gif'

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

    def visSegPng(self, image_template=None, mask_template=None, output_template=None, output_prefix='refine_', frame_ids=None, frame_downsample = 4, redo= False):
        if image_template is None:
            image_template = self.data.FRAME_NAME.format(self.data.video_name, '_ds')
        if mask_template is None:
            mask_template = self.data.PROCESSOR_STM.format(self.data.video_name)
        if output_template is None:
            output_template = self.data.PROOFREADER_SEG.format(self.data.video_name, output_prefix)

        if isinstance(frame_ids, str):
            frame_ids = self.data.getFrameIndex(frame_ids)
        vutil.mkdir(output_template, 'dir')
        for frame_id in frame_ids:
            output_name = output_template % frame_id
            mask_name = mask_template % frame_id 
            if os.path.exists(mask_name) and (redo or not os.path.exists(output_name)):
                im = self.data.getFrameImage(frame_id)[::frame_downsample, ::frame_downsample]
                seg = imageio.imread(mask_name)[::frame_downsample, ::frame_downsample]
                imageio.imwrite(output_name, vutil.visSeg(im, seg))
