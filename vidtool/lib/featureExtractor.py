import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from torch.autograd import Variable


class featureExtractor(object):
    def __init__(self, model_name='resnet18', layer_name='avgpool', do_gpu = True):
        self.do_gpu = do_gpu and torch.cuda.is_available()
        # prepare data
        self.scaler = transforms.Scale((224, 224))
        self.normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                         std=[0.229, 0.224, 0.225])
        self.to_tensor = transforms.ToTensor()

        # prepare model 
        self.loadModel(model_name, layer_name)


    def loadModel(self, model_name, layer_name):
        if model_name == 'resnet18':
            self.model = models.resnet18(pretrained=True)
            self.embed_shape = 512
        elif model_name == 'resnet50':
            self.model = models.resnet50(pretrained=True)
            self.embed_shape = 2048
        #self.model = models.resnet18(pretrained=True)
        #self.model = models.vgg19(pretrained=True)
        #self.model = models.mobilenet_v2(pretrained=True)
        #self.model = models.inception_v3(pretrained=True)
        
        if self.do_gpu:
            self.model = self.model.cuda()
        self.model.eval()
        self.my_embedding = torch.zeros(self.embed_shape)
        self.layer = self.model._modules.get(layer_name)
        def copy_data(m, i, o):
            self.my_embedding.copy_(o.data.squeeze())
        h = self.layer.register_forward_hook(copy_data)

    def extractFeature(self, image):
        t_img = Variable(self.normalize(self.to_tensor(self.scaler(image))).unsqueeze(0))
        if self.do_gpu:
            t_img = t_img.cuda()
        self.model(t_img)
        return self.my_embedding.numpy().squeeze().copy()
