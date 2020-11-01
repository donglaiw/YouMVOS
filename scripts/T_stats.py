import os,sys
import json

opt = sys.argv[1]
Dyt='/n/pfister_lab2/Lab/vcg_natural/YouTube-VIS/'
if opt[0] =='0':
    # get stats of other datasets
    if opt == '0':# youtube-vis
        dds = ['vis','vos']
        dds = ['vos']
        for dd in dds:
            cc = [0,0]
            for nn in ['train','valid','test']:
                jj = json.load(open(Dyt + dd + '/' + nn+'.json'))
                import pdb; pdb.set_trace()
                cc[0] += len(jj['videos'])
                cc[1] += sum([x['length'] for x in jj['videos']])
            print(dd, cc)
    elif opt == '0.1':# kitti-mos
        # (5027+2981+2862)/25 
        pass

elif opt[0] =='1':
    if opt == '1': # count fps
        pass

