# rc cluster version
class videoParam(object):
    def __init__(self):
        # folder path
        self.FOLDER_DOWNLOAD = "/n/pfister_lab2/Lab/vcg_natural/YouTop200/{}/"
        self.FOLDER_RELEASE = "/n/pfister_lab2/Lab/vcg_natural/YouTop200/release/"
        # for web annotation
        self.FOLDER_WEB = "/n/boslfs02/LABS/lichtman_lab/glichtman/public/vcg/youtop-vis/youtube/"
        self.FOLDER_WEB2 = "/n/boslfs02/LABS/lichtman_lab/glichtman/public/vcg/youtop-vis/youtube/"
        #self.FOLDER_WEB = "/n/pfister_lab2/Lab/public/YouTop200/"
        # for desktop annotation
        #self.FOLDER_VAST = "/n/boslfs/LABS/lichtman_lab/Donglai/youtop/share/"
        self.FOLDER_VAST = "/n/pfister_lab2/Lab/donglai/YouTop200/db/share/{}/"

        # library path
        self.LIB_DETECTRON2 = "/n/pfister_lab2/Lab/donglai/lib/pipeline/detectron2/"
        self.LIB_STM = "/n/pfister_lab2/Lab/donglai/lib/pipeline/STM/"
        self.LIB_FFMPEG = "/n/home04/donglai/local/bin/ffmpeg "

        # processor filename and path
        self.PROCESSOR_DETECTON2 = self.FOLDER_VAST + "seg/seg_%05d.png" # video name
        self.PROCESSOR_STM = self.FOLDER_VAST + "seg_prop/seg_%05d.png" # video name
        self.PROCESSOR_STM2 = self.FOLDER_VAST + "seg_prop_out/seg_%05d.png" # video name

        # frame filename and path
        self.FRAME_NAME = self.FOLDER_DOWNLOAD + "frame{}/image_%05d.png" # video name, suffix
        self.FRAME_NAME_DS = self.FOLDER_WEB + "frame_ds/{}/image_%05d.png" # video name 
        self.FRAME_NAME_VAST = self.FOLDER_VAST + "im/image_%05d.png" # video name 
        self.FRAME_OFFSET = 1


        # proofreader filename and path
        self.PROOFREADER_ROOT = self.FOLDER_WEB + "proofread/"
        self.PROOFREADER_GIF = self.FOLDER_WEB + "gif/{}_{}.gif" # video_name
        self.PROOFREADER_HTML_TEST = self.PROOFREADER_ROOT + "%s/test/%s%s.html" # video genre, video url, suffix
        self.PROOFREADER_JS_SAVE = self.PROOFREADER_ROOT + "%s/saved/%s%s.js" # video genre, video url, suffix
        self.PROOFREADER_JS_CLUSTER = "_cluster"
        self.PROOFREADER_JS_SHOT = "_shot"
        self.PROOFREADER_SEG = self.FOLDER_WEB + "seg_ds/{}/{}%05d.png" # video_name, prefix, frame_index
