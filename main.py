import configparser
from MOVIESCRIPT import *
from TIKTOKSCRIPT import *

# reddit_main(subreddit, reqlimit, limit) function downloads hot posts from a given subreddit
# reqlimit is the number of posts that is requested in the initial json get. The lower the better, but if too low, then you may not get enough posts to reach 'limit'
# limit is the number of posts you want
# this function will need to be called twice on initialization so that the headers can be created

# movie_main(vidlength, bgcontent, iteration, subreddit) function creates and writes the clip
# bg content is the name of the file that background content should be pulled from
# iteration is for the for loop that is used in this file that cycles through the posts to make the movies
# ex: movie_main(9,'MinecraftParkour',2,'memes')

subredditlist = ['memes','scottishpeopletwitter']

config = configparser.ConfigParser()
config.read('TikTokContentGenerator.ini')

reddit_content_directory = config['filepaths']['rcd']
bgfolderfilepath = config['filepaths']['bgfolderfilepath']
randbgfilepath = config['filepaths']['randbgfilepath']
memefilepath = config['filepaths']['memefilepath']
vidfilepath = config['filepaths']['vidfilepath']

def main():
    header_init()
    redditheadertime = utc_now()
    for j, subreddit in enumerate(subredditlist):
        reddit_main(subreddit,12,3)
        for k, image in enumerate(os.listdir(reddit_content_directory.format(subreddit))):
            movie_main(9,'MinecraftParkour',k,subreddit)
            
if __name__ == '__main__':
    main()