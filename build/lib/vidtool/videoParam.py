# rc cluster version
class videoParam(object):
    def __init__(self):
        # folder path
        self.FOLDER_DOWNLOAD = "/n/pfister_lab2/Lab/vcg_natural/youtubeE-vis/"
        # for web annotation
        self.FOLDER_WEB = "/n/boslfs02/LABS/lichtman_lab/glichtman/public/vcg/youtop-vis/youtube/"
        # for desktop annotation
        self.FOLDER_VAST = "/n/boslfs/LABS/lichtman_lab/Donglai/youtop/share/"

        # library path
        self.LIB_DETECTRON2 = "/n/pfister_lab2/Lab/donglai/lib/pipeline/detectron2/"
        self.LIB_STM = "/n/pfister_lab2/Lab/donglai/lib/pipeline/STM/"
        self.LIB_FFMPEG = "/n/home04/donglai/local/bin/ffmpeg "

        # frame filename and path
        self.FRAME_NAME = self.FOLDER_DOWNLOAD + "{}/frame{}/image_%05d.png" # video name, suffix
        self.FRAME_OFFSET = 1

        # processor filename and path
        self.PROCESSOR_DETECTON2 = self.FOLDER_VAST + "%s/seg_2d/" # video name
        self.PROCESSOR_STM = self.FOLDER_VAST + "{}/seg_prop/seg_%05d.png" # video name
        self.PROCESSOR_VAST_BD = self.FOLDER_VAST + "%s/seg_shot_bd/" # video name
        self.PROCESSOR_REFINE = self.FOLDER_VAST + "%s/seg_refine/" # video name

        # proofreader filename and path
        self.PROOFREADER_ROOT = self.FOLDER_WEB + "proofread/"
        self.PROOFREADER_HTML_TEST = self.PROOFREADER_ROOT + "%s/test/%s%s.html" # video genre, video url, suffix
        self.PROOFREADER_JS_SAVE = self.PROOFREADER_ROOT + "%s/saved/%s%s.js" # video genre, video url, suffix
        self.PROOFREADER_JS_CLUSTER = "_cluster"
        self.PROOFREADER_JS_SHOT = "_shot"
        self.PROOFREADER_SEG = self.FOLDER_WEB + "seg_ds/{}/{}%05d.png" # video_name, prefix, frame_index
