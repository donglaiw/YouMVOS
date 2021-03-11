import os,sys
import json
import numpy as np

from vidtool import videoTool

opt = sys.argv[1]
Dyt='/n/pfister_lab2/Lab/vcg_natural/YouTube-VIS/'
if opt[0] =='0':
    # get stats of other datasets
    if opt == '0':# youtube-vis
        cc = [0,0]
        for nn in ['train','valid','test']:
            jj = json.load(open(Dyt + 'vis/' + nn+'.json'))
            cc[0] += len(jj['videos'])
            cc[1] += sum([x['length'] for x in jj['videos']])
        print('vis', cc)
    elif opt == '0.01':# youtube-vis
        cc = [0,0]
        for nn in ['train','valid']:
            jj = json.load(open(Dyt + '../YouTube-VOS/%s/meta.json'%nn))
            cc[0] += len(jj['videos'])
            cc[1] += sum([max([len(jj['videos'][x]['objects'][y]['frames']) for y in jj['videos'][x]['objects']]) for x in jj['videos']])
        print('vos', cc)

    elif opt == '0.1':# kitti-mos
        # (5027+2981+2862)/25 
        pass

elif opt[0] =='1': # youtube-vos/vis
    vtool = videoTool(0, 1)
    if opt == '1': # download 
        fns = vtool.util.readtxt(Dyt + 'video_url.txt')
        fns = [x[x.find(' ')+1:-1] for x in fns]
        for fn in fns:
            vv = vtool.util.getVideoViews(fn)
            print(fn,vv)
    elif opt == '1.1': # vos
        fns = vtool.util.readtxt(Dyt + 'video_url.txt')
        fns_0 = [x[:x.find(' ')] for x in fns]
        fns_1 = [x[x.find(' ')+1:-1] for x in fns]
        """
        # vis:
        cc=[]
        for mm in ['train','valid','test']:
            dd = json.load(open(Dyt + 'vis/%s.json'%(mm)))
            ytn = [x['file_names'][0][:x['file_names'][0].find('/')] for x in dd['videos']]
            cc += [vtool.util.getVideoViews(fns_1[x]) for x in range(len(fns_0)) if fns_0[x] in ytn] 
        cc = np.array(cc)
        print('vis', cc[cc>=0].mean())
        """
        # vos:
        cc=[]
        for mm in ['train','valid']:
            dd = json.load(open(Dyt + '../YouTube-VOS/%s/meta.json'%(mm)))
            ytn = list(dd['videos'].keys())
            cc += [vtool.util.getVideoViews(fns_1[x]) for x in range(len(fns_0)) if fns_0[x] in ytn] 
        cc = np.array(cc)
        print('vos', cc[cc>=0].mean())

