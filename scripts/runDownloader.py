import os,sys,shutil
from vidtool import videoTool
import numpy as np

if __name__ == "__main__":
    opt = sys.argv[1]
    job_id = 0
    job_num = 1
    if len(sys.argv) > 3:
        job_id = int(sys.argv[2])
        job_num = int(sys.argv[3])

    vtool = videoTool(job_id, job_num)

    fn = 'data/video_v1'
    fn = 'data/video_v2'
    fn = 'data/video_v0'
    fn = 'data/video'
    vv=[]
    #vopt=0;vv=['movie_trailer']
    
    if opt[0] in ['1']:
        vtool.data.setInputVideoJson(fn + '.json')
    else:
        vtool.data.setInputVideoTxt(fn + '.txt')

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
                # Download the mp4
                vtool.downloader.downloadVideoMP4()
            elif opt == '0.1':
                # Check video size
                vtool.util.checkVideoSize(vtool.downloader.getVideoPath())
            elif opt == '0.2':
                # Extract frames
                vtool.downloader.extractVideoFrames()
            elif opt == '0.3':
                # Gather video information: txt -> json
                if vid ==0:
                    vtool.util.VideoTxtToJson(fn + '.txt', fn + '.json', vtool.data.FOLDER_DOWNLOAD, vtool.data.FOLDER_DOWNLOAD)
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
                    import pdb; pdb.set_trace()
            elif opt == '1.5': # number of character
                stat[vid] = len(vtool.util.readtxt(vtool.data.FOLDER_DOWNLOAD.format(video_name) + '/seg_all_out.txt'))


    print(stat.mean())
    import pdb; pdb.set_trace()
    # stat.reshape(20,-1).mean(axis=0)
    print(stat[stat>0].mean())
    if opt in ['1.4']:
        ui, uc = np.unique(stat, return_counts=True)
        print(ui,uc)
    if opt in ['1.5']:
        for x in stat[stat>0]:
            print(x)
