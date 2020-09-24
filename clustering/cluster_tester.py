import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from torch.autograd import Variable
from PIL import Image
#from summary import summary
import os
import numpy as np
import shutil
#model = models.resnet18(pretrained=True)
#model = models.vgg19(pretrained=True)
#model = models.mobilenet_v2(pretrained=True)
model = models.resnet50(pretrained=True)
embed_shape = 2048
print(model)
#model = models.inception_v3(pretrained=True)
layer = model._modules.get('avgpool')
#print(layer)
model = model.cuda()
model.eval()
#stop
left = 100
right = 224
top = 0
bottom  = 224
sim = 0.86
scaler = transforms.Scale((224,224))
normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
flip = transforms.RandomHorizontalFlip(p=1)
#flip = transforms.RandomRotation(degrees=(90,-90))
to_tensor = transforms.ToTensor()
#crop((left,top,right,bottom))
def get_embed(Image_1):
    img = Image.open(Image_1)
    t_img = Variable(normalize(to_tensor(flip(scaler(img)))).unsqueeze(0))
    my_embed = torch.zeros(embed_shape)
    #print(my_embed.shape)
    def copy_data(m,i,o):
     my_embed.copy_(o.data.squeeze())
     #my_embed.copy_(o.data.view(-1))

    h = layer.register_forward_hook(copy_data)
    t_img = t_img.cuda()
    model(t_img)
    h.remove()

    return my_embed 

def similarity_function(Image_1,Image_2):


    embedding_1 = get_embed(Image_1)
    embedding_2 = get_embed(Image_2)
    cos = nn.CosineSimilarity(dim=1, eps=1e-6)
    cos_sim = cos(embedding_1.unsqueeze(0),
              embedding_2.unsqueeze(0))
    #print('\nCosine similarity: {0}\n'.format(cos_sim))
    return cos_sim.numpy()[0]


if __name__ == "__main__":
    #print(summary(model,(3,224,224)))
    Image_1 =  'image_00529.png'
    Image_2  = 'image_14137.png'

    print(similarity_function(Image_1,Image_2))