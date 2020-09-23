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
sim = 0.86
scaler = transforms.Scale((224,224))
normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])

to_tensor = transforms.ToTensor()
def get_embed(Image_1):
    img = Image.open(Image_1)
    t_img = Variable(normalize(to_tensor(scaler(img))).unsqueeze(0))
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
    #Image_1 =  '00000.jpg'
    #Image_2  = '00004.jpg'
    #similarity_funtion(Image_1,Image_2)
    curr_max = 0
     
    image_dir = 'D:/YouTubeTop-vis/cooking/3nUKwvFsjA4/im'
    final_shot_dir = 'D:/YouTubeTop-vis/cooking/3nUKwvFsjA4/final_shots'
    os.chdir(final_shot_dir)
         #os.chdir(common_mask_dir)
    for dir_name in os.listdir(final_shot_dir):
        final_shot_dir_curr = os.path.join(final_shot_dir,dir_name)
        for filename in os.listdir(final_shot_dir_curr):
          file_path = os.path.join(final_shot_dir,filename)
          
          try:
              os.remove(file_path)   

          except OSError:
            print('nahi ho rha 1')
            pass
        shutil.rmtree(final_shot_dir_curr)    
    shot_count = 0
    current_shot_head_array = []
    done = False
    for file_name in os.listdir(image_dir):
        done = False
        file_path = os.path.join(image_dir,file_name)
        #curr_max = 0
        #save_path = 'l'
        for shot_list in os.listdir(final_shot_dir):
            if done==True:
                break
            similarity = 0
            
            try:
             shot_list_path = os.path.join(final_shot_dir,shot_list)
             shot_list_frames = os.listdir(shot_list_path)
             shot_head_path = os.path.join(shot_list_path,shot_list_frames[0])
             print(shot_head_path)
             similarity = similarity_function(file_path,shot_head_path)
             print(similarity)
            except OSError:
                print('no_similarity')
                pass 
            
            if similarity>sim:
            #if similarity>curr_max:
                #curr_max = similarity
                #save_path = shot_list_path
                done  = True
                d = Image.open(file_path)
                d.save(os.path.join(shot_list_path,file_name))
        #if curr_max>0.85:
         #   done = True
          #  d = Image.open(file_path)
           # d.save(os.path.join(save_path,file_name))
       
        if done==False:
            d = Image.open(file_path)
            new_shot_path = os.path.join(final_shot_dir,str(shot_count))
            os.mkdir(new_shot_path)
            new_file_path = os.path.join(new_shot_path,file_name)
            d.save(new_file_path)
            shot_count+=1

    

