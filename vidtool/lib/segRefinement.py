from scipy.ndimage.morphology import binary_erosion, binary_dilation
import cv2

class SegRefinement(object):
    def __init__(self):
    
    
    def setGrabCut(self, erode_ratio=0.9, iter_seg = [2, 20], iter_algo = 5,\
                    alpha_fade=1):
        self.gc_erode_ratio = erode_ratio
        self.gc_iter_seg = iter_seg
        self.gc_iter_algo = iter_algo
        self.gc_alpha_fade = alpha_fade

    def erodeForeground(self, seg_fg, gc_iter_seg = [2,20], erode_rate = 0.9):
        seg_fg = binary_erosion(seg_fg, iterations = gc_iter_seg[0])
        instance_pixs = float(seg_fg.sum())
        for i in range(gc_iter_seg[0] + 1, gc_iter_seg[1]):
              seg_fg = binary_erosion(seg_fg)
              if seg_fg.sum()/instance_pixs < erode_ratio: break
        return seg_fg

    def fadeBackground(self, img, back, alpha = 0.6):
        if alpha == 1:
            return img
        neg_gray = np.where(back == 0, 1., 0.)
        pos_gray = 1 - neg_gray
        nm = img * neg_gray[:, :, None]
        m = img * pos_gray[:,:, None]
        imx = np.uint8(m + nm*alpha)
        return imx

    def refineGrabcut(im, seg): 
        seg_new = None
        if seg.max() > 0:
            sz = im.shape
            uid = np.unique(seg)
            uid = uid[uid>0]
            bgdModel = np.zeros((1,65),np.float64)
            fgdModel = np.zeros((1,65),np.float64)
            mask = np.zeros(sz[:2], np.uint8)
            seg_new = np.zeros(sz[:2], seg.dtype)
            for i in uid:
                mask[:] = 0
                
                # foreground 1: erode mask until 90%
                mask_fg = self.erodeForeground(seg == i, self.gc_iter_seg, self.gc_erode_ratio)
                mask[mask_fg] = 1
                
                imx = self.fadeBackgrnd(im, mask, self.gc_alpha_fade)

                # maybe foreground 3: dilate fg by gc_iter_image[0]
                mask_in = binary_dilation(mask == 1, iterations = self.gc_iter_seg[0])
                mask[(mask_in > 0) * (mask == 0)] = 3

                # maybe background 2: dilate orig mask by gc_iter_image[0]
                mask_dilation = binary_dilation(seg == i, iterations = self.gc_iter_seg[0])
                mask[(mask_dilation > 0) * (mask == 0)] = 2


                out, bgdModel, fgdModel = cv2.grabCut(im, mask, None, bgdModel, fgdModel, iter_algo, cv2.GC_INIT_WITH_MASK)
                out2 = np.where((out == cv2.GC_BGD) | (out == cv2.GC_PR_BGD), 0, 1)
                seg_new[out2 > 0] = i
        return seg_new

    def convertClusterStrToClusterList(cluster_str):
        if cluster_str[-1] == ';':
            cluster_str = cluster_str[:-1]
        cluster_list = [[int(y) for y in x.split(',')] for x in cluster_str.split(';')]
        return cluster_list

    def convertClusterListToStr(shots):
        return ';'.join([','.join([str(y) for y in shots[x]]) for x in range(len(shots))]) 

    def convertClusterListToJs(shots):
        cluster_str = convertClusterListToStr(shots)
        output_js = 'var shot_index_str="' + cluster_str + '";'
        output_js += 'var shot_selection_str="0";'
        return output_js

    def copyFolder(input_folder, output_folder, file_ext='png', name_replace=[], frame_downsample=1):
        mkdir(output_folder)
        files_in = glob.glob(input_folder + '/*.' + file_ext)
        files_out = glob.glob(output_folder + '/*.' + file_ext)
        if len(files_in)>0 and len(files_out)!=len(files_in):
            print('copy')
            for file_in in files_in:
                file_out = file_in[file_in.rfind('/')+1:]
                if len(name_replace) != 0:
                    file_out = file_out.replace(name_replace[0], name_replace[1])
                file_out = output_folder + file_out
                if not os.path.exists(file_out):
                    if frame_downsample == 1:
                        shutil.copyfile(file_in, file_out)
                    else:
                        output = imageio.imread(file_in)[::frame_downsample, ::frame_downsample]
                        imageio.imwrite(file_out, output)

    def visSeg(im, seg, option=0):
        alpha = 0.7
        if seg.ndim == 3:
            seg = seg[:,:,2]
        if option == 0: # gray image
            # to keep the color label consistent
            # make sure all indices are present
            # hack the first elements 
            seg_mid = seg.max()
            prev_val = seg[0,:seg_mid].copy()
            seg[0,:seg_mid] = range(seg_mid) 
            seg_color = label2rgb(seg, bg_label=0)
            seg_color[0,:seg_mid] = seg_color[0,prev_val]
            im_gray = rgb2gray(im)[:,:,None]
            output = (255*(alpha * im_gray + (1 - alpha) * seg_color)).astype(np.uint8)
            return output 
        elif option == 1: # original image
            out = im.copy()
            seg_colored = 255.*label2rgb(seg, colors = COLOR64)
            seg_mask = np.tile(seg[:, :, None]>0, [1,1,3])
            out[seg_mask] = (im[seg_mask].astype(float) * frame_alpha + seg_colored[seg_mask] * (1 - frame_alpha)).astype(np.uint8)
            return out
