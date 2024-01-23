import os,sys,shutil
import argparse
from vidtool import videoTool
import numpy as np
def get_args():
    parser = argparse.ArgumentParser(description='Semi-automatic video object segmentation')
    parser.add_argument('-v','--video', type=str, default='data/video_rest.txt',
                       help='txt file for video url and category label')
    parser.add_argument('-p','--param', type=str, default='data/param.txt',
                       help='txt file for project parameters')
    parser.add_argument('cmd', type=str, default='',
                       help='command to execute')
    parser.add_argument('-jid','--job-id', type=int, default=0,
                       help='job id')
    parser.add_argument('-jnum','--job-num', type=int, default=1,
                       help='job number')
    parser.add_argument('--redo', action='store_true',
                       help='redo')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = get_args()

    if args.cmd == '':
        raise Exception("No command entered.")

    vtool = videoTool(args.video, args.param)
    vtool.setRedo(args.redo)

    vtool.process(args.cmd, args.job_id, args.job_num)

   
    """
    if opt[0] in ['1']:
        vtool.data.setInputVideoJson(fn + '.json')

    stat = np.zeros(len(vtool.data.video_all_name[job_id::job_num]), int)

    for vid,video_name in enumerate(vtool.data.video_all_name[job_id::job_num]):
        video_genre = video_name[:video_name.rfind('/')]
        video_url = video_name[video_name.rfind('/')+1:]
        if len(vv) > 0 :
            if vopt == 0:
                if video_genre not in vv:
                    continue
            elif vopt == 1:
                if video_url not in vv:
                    continue

        print(video_name)
        vtool.data.setVideoInfo(video_name)

        if opt[0] == '0':
            if opt == '0':
                # Download the mp4 -f 136
            elif opt == '0.1':
                # Check video size
                vtool.util.checkVideoSize(vtool.downloader.getVideoPath())
            elif opt == '0.2':
                # Extract frames
                vtool.downloader.extractVideoFrames()
            elif opt == '0.3':
                # Gather video information: txt -> json
                if vid ==0:
                    vtool.util.VideoTxtToJson(fn + '.txt', fn + '.json', vtool.data.FOLDER_DOWNLOAD[:-3], vtool.data.FOLDER_DOWNLOAD[:-3])
                break;
            elif opt == '0.31': # generate js param for visualization file
                vtool.util.VideoTxtToJs(fn + '.txt', vtool.data.FOLDER_WEB + 'js/%s.js' % fn[fn.rfind('/')+1:])
                break
        elif opt[0] == '1':
            if opt == '1': # sanity check for the number of frames
                t1 = vtool.data.video_all_info[video_name]['fps'] * vtool.data.video_duration  
                t2 = vtool.data.video_frame_num
                if np.abs(t1-t2)>4:
                    print(t1,t2)
                stat[vid] = t2
            elif opt == '1.1': # get count statistics
                video_url = video_name[video_name.rfind('/')+1:]
                stat[vid] = vtool.util.getVideoViews(video_url)
            elif opt == '1.2': # get length
                stat[vid] = vtool.data.video_duration
            elif opt == '1.3': # num shots
                fn = vtool.data.FOLDER_DOWNLOAD.format(video_name) + 'shot.txt'
                if os.path.exists(fn):
                    stat[vid] = np.loadtxt(fn).shape[0]

            elif opt == '1.4': # fps
                stat[vid] = int(np.round(vtool.data.video_all_info[video_name]['fps']))
                if stat[vid] == 27:
                    pass
                    import pdb; pdb.set_trace()
            elif opt == '1.5': # number of character
                stat[vid] = len(vtool.util.readtxt(vtool.data.FOLDER_DOWNLOAD.format(video_name) + '/seg_all_out.txt'))


    print(stat.mean())
    import pdb; pdb.set_trace()
    #import pdb; pdb.set_trace()
    # stat.reshape(20,-1).mean(axis=0)
    print(stat[stat>0].mean())
    if opt in ['1.4']:
        ui, uc = np.unique(stat, return_counts=True)
        print(ui,uc)
    if opt in ['1.5']:
        for x in stat[stat>0]:
            print(x)
    """
