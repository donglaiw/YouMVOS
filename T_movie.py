import os,sys
import numpy as np
sys.path.append('../')
from T_util import readh5,writeh5

opt=sys.argv[1]
job_id=0;job_num=1

if len(sys.argv)>3:
    job_id = int(sys.argv[2])
    job_num = int(sys.argv[3])

Dv='/n/pfister_lab2/Lab/vcg_natural/movies/'
mns=['Harry_Potter_1']
mnLs=[228507]
mnSs=[[798,1920]]
# start - end
mnFs=[[5904,216646]]
mid=0

mn=mns[mid];
mnL=mnLs[mid];
mnS=mnSs[mid];
mnF=mnFs[mid];
foset=1 # ffmpeg: start from frame 1

# ffmpeg -i image09d.png
def fid2name(fid,suf='png'):
    return '/%d/image%09d.%s'%(fid//1000,fid,suf)

def get_im(fid):
    return imread(Dv+'frames/'+mn+fid2name(fid))
# for i in {0..228};do mkdir new/${i};done
# for i in {0..228};do echo "do ${i}"; for j in {000..999};do mv image`printf "%06d" ${i}`${j}.png ${i}/;done;done
if opt[0]=='0': # movie -> clips
    from scipy.misc import imread,imsave
    numF=1000
    numC = (mnL+numF-1)//numF
    if opt=='0': # get mean
        for fid in range(1,mnL+1)[job_id::job_num]:
            sn = Dv+'stat/'+mn+'/rgb_m/'+fid2name(fid,'txt')
            if not os.path.exists(sn):
                np.savetxt(sn,[get_im(fid)[::4,::4].mean()],'%d')
    elif opt=='0.01': # get change
        numC = (mnL+job_num-1)//job_num
        f1=-1
        im1=None
        for fid in range(1,mnL+1)[job_id*numC:min((job_id+1)*numC,mnL-1)]:
            sn = Dv+'stat/'+mn+'/rgb_dif/'+fid2name(fid,'txt')
            if not os.path.exists(sn):
                im2 = get_im(fid+1)[::4,::4].astype(float)
                if f1!=fid:
                    im1 = get_im(fid)[::4,::4].astype(float)
                dif = np.abs(im1-im2).mean()
                np.savetxt(sn, [dif],'%d')
                f1 = fid+1
                im1[:] = im2
    elif opt=='0.09': # get result per chunk
        kk = 'rgb_dif';delta=-1
        #kk = 'rgb_m';delta=0
        for z in range(numC)[job_id::job_num]:
            sn = Dv+'stat/'+mn+'/%s/%d.txt'%(kk,z)
            if not os.path.exists(sn):
                print(sn)
                zz = range(max(1,z*numF), min((z+1)*numF,mnL+1+delta))
                out=np.zeros(len(zz),int)
                for zi in zz:
                    fn = Dv+'stat/'+mn+'/%s/%s'%(kk,fid2name(zi,'txt'))
                    out[zi-zz[0]] = np.loadtxt(fn)
                np.savetxt(sn,out,'%d')
    elif opt=='0.091': # get result
        kk = 'rgb_m'
        kk = 'rgb_dif'
        sn = Dv+'stat/'+mn+'/%s.h5'%(kk)
        if not os.path.exists(sn):
            out=[None]*numC
            for z in range(numC):
                out[z] = np.loadtxt(Dv+'stat/'+mn+'/%s/%d.txt'%(kk,z))
            writeh5(sn,np.hstack(out).astype(np.uint8))
    elif opt=='0.1': # scene detection
        # find non-zero regions
        # not useful..
        from skimage.measure import label
        th_dark = 10 
        th_len = 10 
        rgb_m = readh5(Dv+'stat/'+mn+'/rgb_m.h5')
        scene = label(rgb_m>th_dark)
        numS = scene.max()
        out = np.zeros([numS,2])
        for sid in range(1,numS+1):
            ind = np.where(scene==sid)[0]
            if len(ind)>th_len:
                out[sid-1] = [ind[0],ind[-1]]
            else:
                print(ind)
                np.savetxt(Dv+'stat/'+mn+'/scene.txt',out[out[:,1]!=0],'%d')
    elif opt=='0.11': # scene selection
        scene = np.loadtxt(Dv+'stat/'+mn+'/scene.txt').astype(int)
        Do=Dv+'stat/'+mn+'/www/scene/%d_%d.png'
        for i in range(scene.shape[0]):
            for j in range(2):
                imsave(Do%(i,j),get_im(scene[i,j])[::4,::4])
    elif opt=='0.12': # shot detection
        # find change
        from skimage.measure import label
        th_dif = 10 # half sec
        th_shot = 12 # half sec

        # ideal: 0s surround the peak
        # if not sure, connect things
        # also remove small ones

        rgb_dif = readh5(Dv+'stat/'+mn+'/rgb_dif.h5')
        bp = np.where(rgb_dif>=th_dif)[0] 
        bp = bp[(bp>mnF[0])*(bp<mnF[1])]

        ind = bp+np.arange(-th_shot,th_shot+1).reshape([-1,1])
        gid = np.array([mnF[0]-1]+list(bp[(rgb_dif[ind]>=th_dif).sum(axis=0)==1])+[mnF[1]])
        out = np.vstack([gid[:-1]+1, gid[1:]]).T
        
        np.savetxt(Dv+'stat/'+mn+'/shot.txt', out+foset,'%d')
    elif opt=='0.121': # shot gif
        from T_util import writegif_vold 
        shot = np.loadtxt(Dv+'stat/'+mn+'/shot.txt').astype(int)
        numF = 5
        out=np.zeros([numF,160,384,3],np.uint8)
        Do=Dv+'stat/'+mn+'/www/shot/%d.gif'
        for i in range(shot.shape[0])[job_id::job_num]:
            if not os.path.exists(Do%i):
                ll = np.linspace(shot[i,0],shot[i,1],numF).astype(int)
                for j in range(numF):
                    out[j] = get_im(ll[j])[::5,::5]
                writegif_vold(Do%i,out,duration=0.2)
