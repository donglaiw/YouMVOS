import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from torch.autograd import Variable
from PIL import Image
import os
import numpy as np
import shutil
from scipy.spatial.distance import cdist 
from glob import glob
from .featureExtractor import featureExtractor

class frameCluster(object):
    def __init__(self, image_list = None, frame_rate = 1):
        self.feature_extractor = featureExtractor()
        self.setInfo(image_list, frame_rate)

    def setInfo(self, image_list, frame_rate = 1):
        if isinstance(image_list, str): # if input the folder+*.png
            self.image_list = sorted(glob(image_list))
        else:
            self.image_list = image_list
        self.frame_rate = frame_rate

    def clusterIdToStr(self, cluster_ids): 
        return ';'.join([','.join([str(1+self.frame_rate*y) for y in np.where(cluster_ids==x)[0]]) for x in np.unique(cluster_ids)]) 

    def getClusterId(self, sim_nn=0.86, sim_small=[5,0.8], metric ='cosine'):
        # first pass: get initial cluster centers
        cluster_ids, cluster_centers = self.FrameToCluster(sim_nn, metric)
        #print(self.clusterIdToStr(cluster_ids))
        # second pass: refine cluster assignment
        cluster_ids, cluster_mean = self.ClusterRefinement(cluster_centers, metric)
        #print(self.clusterIdToStr(cluster_ids))
        # thrid pass: try to assign small clusters
        cluster_ids = self.MergeSmallCluster(cluster_ids, cluster_mean, cluster_centers, sim_small, metric)
        #print(self.clusterIdToStr(cluster_ids))
        return cluster_ids

    def MergeSmallCluster(self, cluster_ids, cluster_mean, cluster_centers, thres_sim=[5,0.82], metric='cosine'): # first pass: assign images to clusters
        ui, uc = np.unique(cluster_ids, return_counts=True)
        cluster_id_small = ui[uc<=thres_sim[0]]
        for i in cluster_id_small:
            similarity = self.getSimilarity(cluster_mean[i:i+1], cluster_mean, metric)
            similarity = np.maximum(similarity, self.getSimilarity(cluster_centers[i:i+1], cluster_mean, metric))
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
            cluster_mean[cluster_ids[i]] += embedding[0]
        ui, uc = np.unique(cluster_ids, return_counts=True)
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
                cluster_ids[i] = cluster_centers.shape[0]
                cluster_centers = np.vstack([cluster_centers, embedding])
        return cluster_ids, cluster_centers
                
    def getEmbeddingFromName(self, image_name):
        return self.getEmbedding(Image.open(image_name))

    def getEmbedding(self, image):
        return self.feature_extractor.extractFeature(image).reshape(1,-1)

    def getSimilarity(self, embedding1, embedding2, metric = 'cosine'):
        if metric == 'cosine':
           dist = 1 - cdist(embedding1, embedding2, metric).squeeze() 
        return dist

