from T_util import readtxt, U_mkdir

class videoDownloader(object):
    def __init__(self, job_id = 0, job_num = 1, output_folder = None, redo = False):
        self.job_id = job_id
        self.job_num = job_num
        self.output_folder = output_folder
        self.redo = redo

    def setSingleProcess(self):
        self.job_id = 0
        self.job_num = 1

    def setRedo(self, redo):
        self.redo = redo

    def setOutputFolder(self, output_folder):
        self.output_folder = output_folder

    def setInputVideoTxt(self, input_file):
        self.checkVideoListFormat(input_file)
        self.input_video_ = readtxt(input_file)

    def parseVideoTxt(self, input_txt):
        input_video = readtxt(input_txt)
        self.video_urls = [None] * len(input_video)
        self.video_genres = [None] * len(input_video)
        for line_id, line in enumerate(input_video):
            tmp = line.split(',')
            self.video_genres[line_id] = tmp[0]
            self.video_urls[line_id] = tmp[1]

    def getVideoInfo(self, video_url):
        output_file = 'tmp/ccv_%d' % self.job_id 
        os.system('ffprobe %s > %s 2>&1' % (video_url, output_file))
        os_out = readtxt(output_file)
        info = [os_line for os_line in os_out if '[SAR 1:1' in os_line][0]
        info_s = info.split(',')
        sz = [x.strip().split(' ')[0] for x in info_s if '[SAR 1:1' in x][0]
        fps = [x.strip().split(' ')[0] for x in info_s if 'fps' in x][0]
        return sz, fps

    def checkVideoListFormat(self, input_file):
        # genre, video_url, author, title 
        videos = readtxt(input_file)
        for line in videos:
            tmp = line.split(',')
            if len(tmp) != 4:
                print("each line should be: genre, video_url, author, title") 
                raise ValueError('Wrong input format: ', line)

    def checkVideoSize(self, input_file):
        for line in videos:
            tmp = line.split(',')
            video = Dv+tmp[0]+'.mp4'
            if os.path.exists(video):
                sz, _ = getVideoInfo(video)
                if '1280x' not in sz:
                    print(tmp[0],sz)

    def getVideoMP4(self, video_urls = None, video_genres = None):
        if self.output_folder is None:
            raise ValueError('Need to set the output folder before downloading videos')

        if video_urls is None:
            if self.input_video is None:
                raise ValueError('need to set video list file before downloading videos')

        if video_genres is None:
            video_genres = [''] * len(video_urls)
        
        video_urls = video_urls[self.job_id :: self.job_num]
        video_genres = video_genres[self.job_id :: self.job_num]

        for video_id in range(len(video_urls)):
            video_url = video_urls[video_id]
            video_genre = video_genres[video_id]
            file_mp4 = self.output_folder + '%s/%s.mp4' % (video_genre, video_url) 
            if not os.path.exists(file_mp4):
                # 136: 1280x720
                cmd = "youtube-dl --no-check-certificate -f 136 " + video_url + " -o " + file_mp4
                print(cmd)
                U_mkdir(file_mp4, 1)
                os.system(cmd)

