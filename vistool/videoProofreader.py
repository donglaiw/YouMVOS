import os,sys
import math
import numpy as np
from glob import glob
import json
import shutil

sys.path.append('/home/donglai/code/')

from T_util import readtxt,writetxt,U_mkdir,arrToStr
opt = sys.argv[1]

class videoProofreader(object):
    def __init__(self, job_id = 0, job_num = 1, redo = False):
        self.job_id = job_id
        self.job_num = job_num
        self.redo = redo

    def setFolders(self, data_folder, web_folder, output_folder):
        # original mp4/frames
        self.data_folder = data_folder
        self.web_folder = web_folder
        self.output_folder = output_folder

    def setInputVideoJson(self, input_file):
        self.checkVideoListFormat(input_file)
        self.input_video_ = readtxt(input_file)
        self.video_info = json.load(open(input_file))
        self.video_name = videos_dict.keys()




Dv = '/mnt/pfister_lab2/vcg_natural/youtubeE-vis/'
Dc = '/mnt/pfister_lab2/donglai/movie-vis/db/export/'
Dg = '/home/donglai/google-drive/YouTubeTop-vis/'
suf='_todo'
#video_todo = ['music_video/RB-RcX5DS5A','kid/F4tHL8reNCs','sports/wgVOgGLtPtc','history/Yocja_N5s1I','howto/j2C8MkY7Co8','vlog/0oPa3GJJDDA','product/dfToHzOmwdI','comedy/qVMW_1aZXRk','cooking/3nUKwvFsjA4','animation/KYniUCGPGLs']

for video in video_todo:
    print('process: ', video)
    mn = video[:video.find('/')+1]
    sn = video[video.find('/')+1:]
    Ds='/var/www/html/donglai/movie/%s/'%mn
    def get_imN(fid): # plus one offset [ffpmeg frame extraction]
        return Dc+'%s/%s/frame_ds/image_%05d.png'%(mn,sn,fid+1)

    def get_shot():
        return np.loadtxt(Dv+'%s/%s/shot.txt'%(mn,sn)).astype(int)

    def get_stat():
        return json.load(open(Dv+'data/video%s.json'%suf))[mn+sn]

    stat = get_stat()

    # copy data: for i in {38,51,54};do cp -r /mnt/pfister_lab2/vcg_connectomics/human/roi466/mito/cell16nm/cell${i}/ cell${i}/ & done
    if opt=='-1':# make folder
        U_mkdir(Ds+'saved/')
        os.chmod(Ds+'saved/', 0o777)
        U_mkdir(Ds+'test/')
        U_mkdir(Ds+'result/')

    elif opt[0]=='2':# copy data to google drive
        if opt == '2':
            sn = Dg + video + '/'
            if not os.path.exists(sn + 'im.vsvi'):
                print('copy:', video)
                shutil.copytree(Dc+'db/detectron2/%s/'%(video), sn)
        elif opt == '2.1':
            import shutil
            from glob import glob
            seg = Dg + video + '/seg/'
            fns = glob(seg+'*.png')
            for fn in fns:
                shutil.move(fn, fn.replace('_s','seg_'))
        elif opt == '2.2': # copy result
            outN = Ds+'../result/%s/' % mn
            U_mkdir(outN)
            if not os.path.exists(outN + '%s_o.gif'%sn):
                shutil.copy(Dv+'%s/%s/www/%s_o.gif'%(mn, sn, sn), outN)
        elif opt == '2.3': # copy proofread shot
            fps = int(np.round(float(stat['fps'])))
            numF = stat['num_frame']
            # copy shot list
            frame_last = (numF // fps)
            result = readtxt(Ds+'saved/%s_shot.js'%sn)[0].split('"')
            shot_start = np.array([int(x) for x in result[1].split(',')])
            shot_selection = np.array([int(x) for x in result[3].split(',')])
            shot = np.vstack([shot_start,list(shot_start[1:]-1)+[frame_last]]).T
            shot_proofread = 1 + shot[shot_selection==0] * fps
            #outN = Ds+'../result/%s/%s_shot.txt' % (mn, sn)
            outN = Dv+'/%s/%s/shot_proofread.txt' % (mn, sn)
            np.savetxt(outN, shot_proofread, '%d')

        elif opt == '2.4': # copy seg result
            # copy seg image
            fid = np.loadtxt(Ds+'../download/%s/%s/fid.txt' % (mn, sn)).astype(int)
            fns = sorted(glob(Dg+'%s/%s/seg_out/*.png' % (mn, sn)))
            assert len(fid) == len(fns)
            outN_s = Dv+'/%s/%s/' % (mn, sn)
            outN = 'db/%s/%s/seg_out/' % (mn, sn)
            U_mkdir(outN)
            outN += 'seg_%05d.png'
            for i in range(len(fid)):
                if not os.path.exists(outN % fid[i]):
                    shutil.copy(fns[i], outN % fid[i])
                    #print('sudo cp '+fns[i] + ' ' + (outN % (fid[i]+1)))
            print('sudo cp -r ' + outN[:outN.rfind('/')] + ' ' + outN_s)


    elif opt[0]=='0':# scene detection
        if opt == '0': # copy html/js
            shutil.copy(Dc+'%s/%s/%s_shot.html'%(mn, sn, sn), Ds+'test/')
            try:
                shutil.copy(Dc+'%s/%s/%s_shot.js'%(mn, sn, sn), Ds+'saved/')
                # make it updatable
                os.chmod(Ds+'saved/%s_shot.js' % sn, 0o777)
            except:
                print('Already done: %s/%s' % (mn, sn))
        elif opt == '0.1': # copy images
            Do = Ds + '../download/%s/%s/'%(mn,sn)
            U_mkdir(Do)
            fps = int(np.round(float(stat['fps'])))
            numF = stat['num_frame']
            frames = np.arange(0, numF, fps)
            for i in frames:
                imN = get_imN(i)
                if not os.path.exists(Do+imN[imN.rfind('/')+1:]):
                    shutil.copy(imN, Do)
    elif opt[0]=='1':# tutorial
        U_mkdir(Ds)
        if opt == '1':#make folder
            gif_folder = Ds+'data/%s/'%(sn)
            if not os.path.exists(gif_folder):
                shutil.copytree(Dv+'%s/%s/www/shot/'%(mn,sn), gif_folder)

            # generate test pages
            total = len(glob(gif_folder+'/*.gif'))
            bcolor='["green","red","white"]';
            Dss = Ds+'test/%s_'%(sn);
            # 1-page for each video
            numC=7
            do_test=False;num=total;outN=Dss+'%d.htm'

            ind=range(total)
            def getImName(im_id):
                return '../data/%s/%d.gif'%(sn,im_id)
            bcolor0=bcolor[bcolor.find('"')+1:bcolor.find(',')-1]
            numP = int(math.ceil(total/float(num)))
            print(sn,numP)

            for pid in range(numP):
                out='<html>'
                out+='<script src="../../../js/jquery-1.7.1.min.js"></script>'
                out+='<ul>'
                out+='<li>green=yes</li>'
                out+='<li>red=no</li>'
                out+='<li>white=not sure</li>'
                out+='</ul>'
                out+="<table cellpadding=8 border=2>"
                pid2 = min((pid+1)*num,total)
                for i in range(pid*num,pid2):
                    if i%numC == 0:
                        out+='<tr>'
                    out+='<td id="t'+str(i-pid*num)+'" class="cc" bgcolor="'+bcolor0+'">'
                    out+='<img height=100 width=150 src="'+getImName(ind[i])+'">'
                    out+='</td>'
                    if (i+1)%numC == 0:
                        out+='</tr>'
                out+="</table>\n"
                out+="<table border=2>\n"
                out+='<tr><td colspan=2><button id="sub" style="width:100%;height=40">Done</button></td><td><p id="score"></p></td></tr>\n'
                #out+='<td align="center"><a id="dw" style="display:none;" href="" download="save_'+str(pid)+'.txt">Download</a></td></tr>'
                out+='</table>'
                out+="""
                      <form id="mturk_form" method="POST" style="display:none">
                         <input id="task" name="task" value=\""""+mn+"""/saved/"""+sn+"""_">
                         <input id="ans" name="ans">
                         <input id="fileId" name="fileId" value="%d">
                     </form>
                    """%(pid)

                # js
                out+='<script>'
                out+="""
                  TOTAL_I="""+str(pid2-pid*num)+""";
                  colors="""+bcolor+""";
                  function get_answer() {
                    var out=new Array(TOTAL_I);
                    for(var i=0;i<TOTAL_I;i++){
                        var cc=$("#t"+i)[0].style.backgroundColor
                        if(cc==""|| cc==colors[0]){
                            out[i]=0;
                        }else if(cc==colors[1]){
                            out[i]=1;
                        }else{
                            out[i]=2;
                        }
                    }
                    return out
                  }
                  $(".cc").click(function(){
                        if($(this)[0].style.backgroundColor=="" || $(this)[0].style.backgroundColor==colors[0]){
                            $(this)[0].style.backgroundColor=colors[1];
                        }else if($(this)[0].style.backgroundColor==colors[1]){
                            $(this)[0].style.backgroundColor=colors[2];
                        }else{
                            $(this)[0].style.backgroundColor=colors[0];
                        }
                  });

                """
                if do_test:
                    out+='gt=['+gt+'];'
                    out+='gtStat=['+','.join([str(gt.count(str(x))) for x in range(2)])+'];'
                    out+="""

                  $("#sub").click(function(){
                      ans_out=get_answer();
                      // local version
                      outStat=[0,0];
                      for(var i=0;i<TOTAL_I;i++){
                        if(gt[i]<2){
                            if(gt[i]==ans_out[i]){
                                outStat[gt[i]] += 1;
                            }
                        }
                      }

                      $("#score").text("Yes: "+outStat[0]+"/"+gtStat[0]+"  No:"+outStat[1]+"/"+gtStat[1]);
                  });
                  """

                else:
                    out+="""
                  $("#sub").click(function(){
                      ans_out=get_answer();
                      document.getElementById("ans").value = ans_out;
                      tmp = $.post("../../save_ans.php", $("#mturk_form").serialize(),function(data) {
                         window.location=window.location.href.substring(0, window.location.href.lastIndexOf("game"));
                       });
                  });
                  """
                out+='</script>'
                out+='<html>'
                a=open(outN%(pid),'w')
                a.write(out)
                a.close()
        elif opt =='1.1':
            from glob import glob
            gb = np.loadtxt(Ds+'saved/%s__0.save'%(sn),delimiter=',').astype(int)
            gb[gb>0]=1
            np.savetxt(Ds+'result/%s_gt.txt'%sn, gb,'%d')

            outN=Ds+'result/%s_g.htm'%(sn)
            do_click=True

            out = '<html>'
            out+='<script src="../../js/jquery-1.7.1.min.js"></script>'
            out+='<ul>'
            out+='<li>green=yes</li>'
            out+='<li>red=no</li>'
            out+='<li>white=not sure</li>'
            out+='</ul>'
            nn=['yes','no','not sure']
            colors=["green","red","white"];
            numC=10
            cc=0
            for vid in [0,1]:
                out+='<hr>'
                nid = np.where(gb==vid)[0]
                out+='<h2>%s (%d)</h2>'%(nn[vid],len(nid))
                out+="<table cellpadding=8 border=2>"
                for i,ii in enumerate(nid):
                    if i%numC == 0:
                        out+='<tr>'
                    out+='<td id="t'+str(cc)+'" class="cc" bgcolor="'+colors[vid]+'">'
                    out+='<img height=100 width=150 src="../data/%s/%d.gif">'%(sn,ii)
                    out+='</td>'
                    cc+=1
                    if (i+1)%numC == 0:
                        out+='</tr>'
                out+="</table>\n"
            out+="<table border=2>\n"
            out+='<tr><td colspan=2><button id="sub" style="width:100%;height=40">Done</button></td>\n'
            out+="</table>\n"
            if do_click:
                # js
                out+='<script>'
                out+="""
                  colors=["green","red","white"];
                  $(".cc").click(function(){
                        var tmp=$(this).attr('bgcolor')
                        if(tmp=="" || tmp==colors[0]){
                            $(this).attr('bgcolor',colors[1]);
                        }else if(tmp==colors[1]){
                            $(this).attr('bgcolor',colors[2]);
                        }else{
                            $(this).attr('bgcolor',colors[0]);
                        }
                  });
                  function get_answer() {
                    var out='';
                    for(var i=0;i<100;i++){
                        var cc=$("#t"+i).attr('bgcolor')
                        if(cc==""|| cc==colors[0]){
                            out+='0,';
                        }else if(cc==colors[1]){
                            out+='1,';
                        }else{
                            out+='2,';
                        }
                    }
                    return out
                  }

                  $("#sub").click(function(){
                      ans_out=get_answer();
                      console.log(ans_out)
                      })
                """
                out+='</script>'
            out+='<html>'
            a=open(outN,'w')
            a.write(out)

        elif opt =='1.2': # get 1fps frames
            Do = Ds + '../download/%s/%s/'%(mn,sn)
            U_mkdir(Do)
            stat = get_stat()
            fps = int(np.round(float(stat['fps'])))
            numF = stat['num_frame']
            frames = np.arange(0, numF, fps)
            gb = np.loadtxt(Ds+'result/%s_gt.txt'%sn).astype(int)
            shot = get_shot()
            if shot.shape[0] != len(shot):
                raise ValueError('mismatch')

            # do plus
            out = []
            for i in np.where(gb==0)[0]:
                out += list(frames[np.in1d(frames,range(shot[i,0], shot[i,1]+1))])
                print(i,len(out))

            np.savetxt(Do+'fid.txt', out, '%d')


        elif opt =='1.3': # initial images for predict and proofread
            Do=Ds+'../download/%s/%s/'%(mn,sn)
            fid = np.loadtxt(Do+'fid.txt').astype(int) + 1
            nn=['im.vsvi','seg.vsvi']
            pref=['.\\','.\\seg\\']
            suf=['','out']
            stat = get_stat()
            im_sz = stat['size']
            for nid in range(len(nn)): 
                out = """{
          "Comment": "Youtube images",
          "ServerType": "imagetiles",

          "SourceFileNameTemplate": \""""+pref[nid]+"""image_%05d"""+suf[nid]+""".png",
          "SourceParamSequence": "s",
          "SourceMinS": 0,
          "SourceMaxS": """+str(stat['num_frame'])+""",
          "SourceMinR": 1,
          "SourceMaxR": 1,
          "SourceMinC": 1,
          "SourceMaxC": 1,

          "MipMapFileNameTemplate": \""""+pref[nid]+"""image_%05d"""+suf[nid]+""".png",
          "MipMapParamSequence": "s",
          "SourceMinM": 0,
          "SourceMaxM": 0,
          """
                out+="""
              "SourceTileSizeX": %d,
              "SourceTileSizeY": %d,
              "SourceBytesPerPixel": 3,
              "MissingImagePolicy": "nearest",
              "SourceSectionOrder": "%s",

              "TargetDataSizeX": %d,
              "TargetDataSizeY": %d,
              "TargetDataSizeZ": %d,
              "OffsetX": 0,
              "OffsetY": 0,
              "OffsetZ": 0,
              "OffsetMip": 0,
              "TargetVoxelSizeXnm": 4.000000,
              "TargetVoxelSizeYnm": 4.000000,
              "TargetVoxelSizeZnm": 4.000000,
              "TargetLayerName": "Youtube"
              }
            """%(im_sz[0],im_sz[1],arrToStr(fid),im_sz[0],im_sz[1],len(fid))
                writetxt(Do+nn[nid], out)
"""
mms = ['masks_comedy','masks_history','masks_kid','masks_music','masks_vlog']
for mm in mms:
    import shutil
    from glob import glob
    seg = Dg + video + '/seg/'
    fns = glob(seg+'*.png')
    for fn in fns:
        shutil.move(fn, fn.replace('_s','seg_'))
"""
