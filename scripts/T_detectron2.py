import os, sys
import numpy as np
sys.path.append('../')
from T_util import U_mkdir,writetxt

opt = sys.argv[1]
D0='/n/pfister_lab2/Lab/donglai/movie-vis/'
if opt[0] == '0':
    # python3
    # sa vis
    # run detectron2: sa detectron2 
    # module load cuda/10.2.89-fasrc01 cudnn/7.6.5.32_cuda10.2-fasrc01 
    # ./tump_run.sh
    import json
    Dv='/n/pfister_lab2/Lab/vcg_natural/youtubeE-vis/'
    #video_dict = json.load(open(Dv+'data/video.json'))
    video_dict = json.load(open(Dv+'data/video_todo.json'))
    video_todo = [*video_dict]
    #video_todo = ['sports/wgVOgGLtPtc','howto/j2C8MkY7Co8','product/dfToHzOmwdI','cooking/3nUKwvFsjA4','animation/KYniUCGPGLs']
    cmds = []
    for video in video_todo:
        stat = video_dict[video]
        fps = int(np.round(stat['fps']))
        num_frame = stat['num_frame']
        frames = 1 + np.arange(0, num_frame, fps)
        inputs_folder = Dv+video+'/frame/image_%05d.png'

        if opt == '0': # copy image
            cmd = 'python /n/pfister_lab2/Lab/donglai/lib/pipeline/detectron2/demo/demo_dw.py --config-file  /n/pfister_lab2/Lab/donglai/lib/pipeline/detectron2/configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml --input-template %s --input-index %s --output %s --opts MODEL.WEIGHTS detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl'
            inputs_index = ','.join([str(x) for x in frames])
            outputs = D0+'db/detectron2/'+video+'/seg/_s%05d.png' 
            U_mkdir(outputs[:outputs.rfind('/')], 2)
            cmds += [cmd % (inputs_folder, inputs_index, outputs)]
            if video == video_todo[-1]:
                writetxt('tmp_run.sh', ['#/bin/bash']+cmds)
        elif opt == '-0.1':
            import shutil
            print('copy 1 fps image: ', video)
            outputs = 'db/detectron2/'+video+'/im/image_%05d.png' 
            U_mkdir(outputs, 2)
            for frame in frames:
                if not os.path.exists(outputs % frame):
                    shutil.copy(inputs_folder % frame, outputs % frame)
