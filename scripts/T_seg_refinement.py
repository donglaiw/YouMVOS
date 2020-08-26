import os,sys
import numpy as np

opt = sys.argv[1]

if opt == '0':
    from imageio import imread,imwrite
    #from scipy.ndimage.morphology import binary_erosion, binary_dilation
    from scipy.ndimage.morphology import binary_erosion, binary_dilation
    # has border artifact
    from scipy.ndimage.morphology import distance_transform_edt
    from skimage.color import label2rgb

    D0 = '/home/donglai/google-drive/YouTubeTop-vis/kid/F4tHL8reNCs/'
    Do = '/var/www/html/donglai/'
    im = imread(D0 + 'im/image_%05d.png' % (1 + 30 * 82))
    seg = imread(D0 + '_s%03d.png' % (82))
    sz = im.shape
    uid = np.unique(seg)
    uid = uid[uid>0]
    img_iter = 30
    algo_iter = 50
    mask = np.zeros(sz[:2], np.uint8)

    dopt = 0 
    if dopt == 0: # grabcut 
        import cv2
        bgdModel = np.zeros((1,65),np.float64)
        fgdModel = np.zeros((1,65),np.float64)
    elif dopt == 1: # grabcut 
        from pymatting import *

    for i in uid:
        mask[:] = 0
        mask_in = binary_erosion(seg == i, iterations = img_iter)
        mask[mask_in > 0] = 1
        mask_in = binary_dilation(seg == i, iterations = img_iter)
        mask[(mask_in > 0) * (mask == 0)] = 3

        dist = distance_transform_edt(seg != i)
        mask[(dist < img_iter * 2) * (mask == 0)] = 2

        if dopt == 0: # grabcut
            out, bgdModel, fgdModel = cv2.grabCut(im, mask, None, bgdModel, fgdModel, algo_iter, cv2.GC_INIT_WITH_MASK)
            out2 = np.where((out == cv2.GC_BGD) | (out == cv2.GC_PR_BGD), 0, 1)
        elif dopt == 1: # matting
            im = im.astype(float)/255.0
            mask = mask.astype(float)
            mask[mask == 1] = 0.5
            mask[mask >= 2] = 1
            alpha = estimate_alpha_cf(im, mask)
            alpha = estimate_alpha_knn(im, mask)
            alpha = estimate_alpha_lbdm(im, mask)
            alpha = estimate_alpha_lkm(im, mask)
            alpha = estimate_alpha_rw(im, mask)
            imwrite(Do + 'alpha%d_gc.png' % i, (alpha*255).astype(np.uint8))
            imwrite(Do + 'alpha%d_gc.png' % i, label2rgb((alpha>0.8c), image=im))
            foreground = estimate_foreground_ml(im, alpha)
            out2 = (foreground.mean(axis=2) > 0.5).astype(np.uint8)

        imwrite(Do + 'seg%d_gc.png' % i, label2rgb(out2, image=im))
        # imwrite(Do + 'seg%d_gc.png' % i, label2rgb((mask*5), image=im))
        # imwrite('seg%d_old.png' % i, label2rgb(seg==i, image=im))
        # imwrite('seg%d_init.png' % i, label2rgb(mask, image=im))
