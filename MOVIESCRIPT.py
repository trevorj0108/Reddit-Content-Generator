import requests
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from moviepy.video.fx.resize import resize
import random
import os
from math import trunc
import multiprocessing
import configparser

config = configparser.ConfigParser()
config.read('TikTokContentGenerator.ini')

bgfolderfilepath = config['filepaths']['bgfolderfilepath']
randbgfilepath = config['filepaths']['randbgfilepath']
memefilepath = config['filepaths']['memefilepath']
vidfilepath = config['filepaths']['vidfilepath']

def background_init(vidlength, bgcontent):
    
    phone_screen_width = 1080
    phone_screen_height = 1920
    bg_path = bgfolderfilepath.format(bgcontent)
    
    randbgfile = os.listdir(bg_path)[random.randint(0,len(os.listdir(bg_path))-1)]
    rand_bg_filepath = randbgfilepath.format(bgcontent,randbgfile)
    bgvideo = VideoFileClip(rand_bg_filepath, audio=False)
    duration = bgvideo.duration
    
    if duration < vidlength:
        print('video too short')
        
    endtime = random.randint(vidlength,trunc(duration))
    bgclip = bgvideo.subclip((endtime-vidlength),endtime)
    
    centerh = int(bgclip.h/2)
    centerw = int(bgclip.w/2)
    maxheight = int(bgclip.h)
    maxwidth = int(maxheight/16)*9
    
    if maxwidth > int(bgclip.w):
        maxwidth = bgclip.w
        
    bgclip = bgclip.crop(x_center = centerw, y_center = centerh, width = maxwidth, height = maxheight)
    bgclip = bgclip.resize((phone_screen_width, phone_screen_height))
    
    return bgclip
    
def image_init(iteration, subreddit, vidlength):
    
    phone_screen_width = 1080
    phone_screen_height = 1920
    scaledwidth = 860
    
    imgclip = ImageClip(memefilepath.format(subreddit, subreddit, iteration)).set_duration(vidlength)
    scalar = scaledwidth/imgclip.w
    scaledheight = scalar*imgclip.h
    imgclip = imgclip.resize((scaledwidth,scaledheight))
    
    return imgclip

def movie_main(vidlength, bgcontent, iteration, subreddit):
        
    background = background_init(vidlength, bgcontent)
    image = image_init(iteration, subreddit, vidlength)
    composite = CompositeVideoClip([background,image.set_position(("center",200))]).set_fps(24)
    composite.write_videofile(vidfilepath.format(subreddit, subreddit, iteration), fps = 24, threads=multiprocessing.cpu_count(), preset = 'veryfast')

