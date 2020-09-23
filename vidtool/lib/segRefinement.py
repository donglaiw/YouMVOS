import numpy as np
import cv2
import matplotlib.pyplot as plt
from pathlib import Path
from skimage.color import label2rgb
from scipy.ndimage.morphology import binary_erosion, binary_dilation, distance_transform_edt
from random import randrange
import re

class RefinementModule:

  def __init__(self, image_list, seg_list, colors = None, alpha_fade = 1, alpha_trans = 0.7, erode_ratio = 0.9, erode_iter = [3, 20]):
    self.images = sorted(image_list)
    self.masks = sorted(seg_list)
    self.clr = np.array(['black', 'blue', 'yellow', 'darkorange', 'magenta', 'cyan', 'yellowgreen', 'red', 'pink', 'indigo', 'green']) if colors == None else colors
    self.alpha_fade = alpha_fade
    self.alpha_trans = alpha_trans
    self.erode_ratio = erode_ratio
    self.pat = re.compile(r'[\d]+')
    self.erode_iter = erode_iter

  def segRefineGrabcut(self, im, seg, iter_algo = 5):
    sz = im.shape
    seg_new = np.zeros(sz[:2], np.uint8)

    if seg.max() > 0:    
        uid = np.unique(seg)
        uid = uid[uid>0]
        bgdModel = np.zeros((1,65),np.float64)
        fgdModel = np.zeros((1,65),np.float64)
        mask = np.zeros(sz[:2], np.uint8)

        for i in uid:
            mask[:] = 0
            eroded_mask, iter_image = self.erodeForeground(seg, i)
            mask[eroded_mask > 0] = 1

            if self.alpha_fade != 1: imx = fadeBackground(im, mask, self.alpha_fade)
            mask_in = binary_dilation(mask == 1, iterations = iter_image)
            mask[(mask_in > 0) * (mask == 0)] = 3
            dist = distance_transform_edt(seg != i)
            mask[(dist < iter_image) * (mask == 0)] = 2
            
            try:
              out, bgdModel, fgdModel = cv2.grabCut(im, mask, None, bgdModel, fgdModel, iter_algo, cv2.GC_INIT_WITH_MASK)
              out2 = np.where((out == cv2.GC_BGD) | (out == cv2.GC_PR_BGD), 0, 1)
              seg_new[out2 > 0] = i
            
            except: 
              continue

    return seg_new

  def erodeForeground(self, seg, val):
    mask_in = binary_erosion(seg == val, iterations = self.erode_iter[0]-1)
    eroded_mask = mask_in
    iter_image = 2
    instance_pixs = np.sum(seg == val)

    for iter in range(self.erode_iter[0], self.erode_iter[1], 2):
      mask_in = binary_erosion(mask_in == val)
      if np.sum(mask_in)/instance_pixs < self.erode_ratio: break
      iter_image = iter
      eroded_mask = mask_in

    return eroded_mask, iter_image

  def fadeBackground(self, img, back, alpha = 0.6):
    neg_gray = np.where(back == 0, 1., 0.)
    pos_gray = 1 - neg_gray

    nm = img * neg_gray[:, :, np.newaxis]
    m = img * pos_gray[:,:, np.newaxis]
    imx = np.uint8(m + nm*alpha)
    return imx

  def overlayMask(self, img, seg, color = 0):
    uid = np.unique(seg)
    ovrl_gray = 255.*label2rgb(seg, img, self.clr[uid[uid > 0]], bg_label = 0)
    if not color: return np.uint8(ovrl_gray)

    seg_mask = np.tile(seg[:, :, None] > 0, [1,1,3])
    seg_neg = np.tile(seg[:, :, None] == 0, [1,1,3])
    imx = np.zeros(img.shape)
    imx[seg_mask] = ovrl_gray[seg_mask]
    imx[seg_neg] = img[seg_neg]
    return np.uint8(imx)

  def visResults(self, img, seg):
    figs, axs = plt.subplots(1, 3, figsize=(25,15))
    ovrl_gray = self.overlayMask(img, seg)
    ovrl_rgb = self.overlayMask(img, seg, 1)
    axs[0].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    axs[1].imshow(cv2.cvtColor(ovrl_gray, cv2.COLOR_BGR2RGB))
    axs[2].imshow(cv2.cvtColor(ovrl_rgb, cv2.COLOR_BGR2RGB))

  def visCompare(self, im, seg, ref_seg):
    vis_ref = np.uint8(np.where(ref_seg > 0, 1, 0))
    vis_seg = np.uint8(np.where(seg > 0, 1, 0))
    out_img = im*vis_ref[:,:,np.newaxis]
    pre_img = im*vis_seg[:,:,np.newaxis]
    imx = self.fadeBackground(im, seg)
    imrx = self.fadeBackground(im, ref_seg)

    figs, axs = plt.subplots(3, 2, figsize=(25,15))
    axs[0, 0].imshow(seg)
    axs[0, 1].imshow(ref_seg)
    axs[1, 0].imshow(cv2.cvtColor(pre_img, cv2.COLOR_BGR2RGB))
    axs[1, 1].imshow(cv2.cvtColor(out_img, cv2.COLOR_BGR2RGB))
    axs[2, 0].imshow(cv2.cvtColor(imx, cv2.COLOR_BGR2RGB))
    axs[2, 1].imshow(cv2.cvtColor(imrx, cv2.COLOR_BGR2RGB))

  def showInput(self):
    index = randrange(0, len(self.masks))
    n_seg = self.pat.search(self.masks[index]).group()
    im = cv2.imread(self.images[int(n_seg)])
    gray = cv2.imread(self.masks[index], 0)
    figs, axs = plt.subplots(1, 2, figsize=(25,15))
    axs[0].imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
    axs[1].imshow(gray)

  def saveResults(self, img, seg, n_seg, n_img, ovl = 1, mask = 1):
    if mask: cv2.imwrite('refined_seg/refined_' + n_seg.zfill(5) + '.png', seg)
    if ovl:  
      h, w, _ = img.shape
      overlay = self.overlayMask(img, seg)
      overlay = cv2.resize(overlay, (w//2, h//2), cv2.INTER_AREA)
      cv2.imwrite('overlays/overlay_' + n_img.zfill(5) + '.png', overlay)

  def refine(self, index, vis = 0):
    n_seg = self.pat.search(self.masks[index]).group()
    im = cv2.imread(self.images[int(n_seg)])
    gray = cv2.imread(self.masks[index], 0)
    gc_out = self.segRefineGrabcut(im, gray, 5)
    if vis: self.visResults(im, gc_out)
    else: return gc_out

  def compareResult(self, index):
    n_seg = self.pat.search(self.masks[index]).group()
    im = cv2.imread(self.images[int(n_seg)])
    gray = cv2.imread(self.masks[index], 0)
    gc_out = self.segRefineGrabcut(im, gray, 5)
    self.visCompare(im, gray, gc_out)

  def refineAll(self):
    self.mapping = {0 : 0}
    for i in range(len(self.masks)):
      n_seg = self.pat.search(self.masks[i]).group()
      n_img = self.pat.search(self.images[int(n_seg)]).group()
      im = cv2.imread(self.images[int(n_seg)])
      gray = cv2.imread(self.masks[i], 0)
      gc_out = self.segRefineGrabcut(im, gray, 5)
      self.saveResults(im, gc_out, n_seg, n_img, mask = 0)