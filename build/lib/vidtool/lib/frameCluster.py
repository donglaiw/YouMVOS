import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from torch.autograd import Variable
from PIL import Image
import os
import numpy as np
import shutil
from scipy.spatial import distance
from glob import glob
from .featureExtractor import featureExtractor
from imageio import imread

class frameCluster(object):
    def __init__(self, image_list = None):
        self.feature_extractor = featureExtractor()
        self.setImageList(image_list)

    def setImageList(self, image_list):
        if isinstance(image_list, str): # if input the folder+*.png
            self.image_list = sorted(glob(image_list))
        else:
            self.image_list = image_list

    def clusterIdToStr(self, cluster_ids): 
        return ';'.join([','.join([str(y) for y in shots[x]]) for x in range(len(cluster_ids))]) 

    def getClusterId(self, sim_nn=0.86, sim_small=[5,0.8], metric ='cosine'):
        # first pass: get initial cluster centers
        cluster_ids, cluster_centers = self.FrameToCluster(sim_nn, metric)
        # second pass: refine cluster assignment
        cluster_ids, cluster_mean = self.ClusterRefinement(cluster_centers, metric)
        # thrid pass: try to assign small clusters
        cluster_ids = self.MergeSmallCluster(cluster_ids, cluster_mean, sim_small, metric)

    def MergeSmallCluster(self, cluster_ids, cluster_mean, thres_sim=[5,0.8], metric='cosine'): # first pass: assign images to clusters
        ui, uc = np.unique(cluster_ids)
        cluster_id_small = ui[uc<=sim_small[0]]
        for i in cluster_id_small:
            similarity = self.getSimilarity(cluster_mean[i], cluster_mean, metric)
            similarity[i] = 0
            if similarity.max() > thres_sim[1]:
                cluster_ids[cluster_ids == i] = np.argmax(similarity)
        return cluster_ids

    def ClusterRefinement(self, cluster_centers, metric='cosine'): # first pass: assign images to clusters
        cluster_ids = np.zeros(len(self.image_list),int) 
        cluster_mean = np.zeros(cluster_centers.shape)
        for i in range(len(self.image_list)): 
            embedding = self.getEmbeddingFromName(self.image_list[i])
            similarity = self.getSimilarity(cluster_centers, embedding, metric)
            cluster_ids[i] = np.argmax(similarity)
            cluster_mean[cluster_ids[i]] += embedding
        ui, uc = np.unique(cluster_ids)
        cluster_mean = cluster_mean / uc.reshape(-1,1)
        return cluster_ids, cluster_mean

    def FrameToCluster(self, thres_sim=0.86, metric='cosine'): # first pass: assign images to clusters
        cluster_ids = np.zeros(len(self.image_list),int) 
        cluster_centers = self.getEmbeddingFromName(self.image_list[0])
        for i in range(1, len(self.image_list)): 
            embedding = self.getEmbeddingFromName(self.image_list[i])
            similarity = self.getSimilarity(cluster_centers, embedding, metric)
            if similarity.max() >= thres_sim:
                cluster_ids[i] = np.argmax(similarity)
            else: # add a new cluster
                cluster_centers = np.vstack([self.cluster_center, embedding])
                cluster_ids[i] = self.cluster_center.shape[0]
        return cluster_ids, cluster_centers
                
    def getEmbeddingFromName(self, image_name):
        return self.getEmbedding(imread(image_name))

    def getEmbedding(self, image):
        return self.feature_extractor.extractFeature(image).numpy().squeeze()

    def getSimilarity(self, embedding1, embedding2, metric = 'cosine'):
        if metric == 'cosine':
           dist = 1 - distance.cosine(embedding1, embedding2) 
        return dist

