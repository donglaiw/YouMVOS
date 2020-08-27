import sys

opt = sys.argv[1]

D0='/n/pfister_lab2/Lab/donglai/movie-vis/'
Do = 'db/slurm/'
sa='source /n/pfister_lab2/Lab/donglai/lib/miniconda2/bin/activate '
sa3='source /n/home04/donglai/miniconda3/bin/activate '
# pp: cox/shared/general
def get_pref(mem=10000,do_gpu=False,pp='cox',tt='4-00:00'):
    pref = '#!/bin/bash\n'
    pref+='#SBATCH -N 1 # number of nodes\n'
    #pref+='#SBATCH -p shared\n'
    pref+='#SBATCH -p %s\n'%pp
    pref+='#SBATCH -n 1 # number of cores\n'
    pref+='#SBATCH --mem '+str(mem)+' # memory pool for all cores\n'
    if do_gpu:
        pref+='#SBATCH --gres=gpu:1 # memory pool for all cores\n'
    pref+='#SBATCH -t %s # time (D-HH:MM)\n'%tt
    return pref


cmd=[]
mem=10000
do_gpu= False
pp = 'cox';tt = '4-00:00'
if opt =='0': 
    fn='movie'
    suf = ' \n'
    num = 10;cn = 'T_movie.py 0'
    num = 10;cn = 'T_movie.py 0.01'
    num = 5;cn = 'T_movie.py 0.09'
    num = 10;cn = 'T_movie.py 0.121'
    num = 10;cn = 'T_movie.py 0.121'
    
    cmd+=[sa+' idm \n']
    cmd+=['ls;python '+D0+cn+' %d '+str(num)+suf]

elif opt =='1': 
    fn='yt'
    suf = ' \n'
    num = 5;cn = 'scripts/runDownloader.py 0.2'
    num = 7;cn = 'scripts/runProofreader.py 0'
    num = 9;cn = 'scripts/runProcessor.py 0.2'
    
    cmd+=[sa3 + ' vis \n']
    cmd+=['ls;python '+D0+cn+' %d '+str(num)+suf]


pref=get_pref(mem, do_gpu, pp, tt)+"""
#SBATCH -o """+Do+"""slurm.%N.%j.out # STDOUT
#SBATCH -e """+Do+"""slurm.%N.%j.err # STDERR

"""
for i in range(num):
    a=open(Do + fn+'_%d.sh'%(i),'w')
    a.write(pref)
    for cc in cmd:
        if '%' in cc:
            a.write(cc%i)
        else:
            a.write(cc)
    a.close()

print(('for i in {0..%d};do sbatch '+Do+'%s_${i}.sh && sleep 1;done')%(num-1, fn))
