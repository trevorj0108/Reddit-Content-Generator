import requests
import json
import os
import pandas as pd
from datetime import datetime, timezone
import time
import configparser
from PIL import Image


def header_init():
    
    config = configparser.ConfigParser()
    config.read('TikTokContentGenerator.ini')
    
    usern = config['redditaccount']['username']
    passw = config['redditaccount']['password']
    client_id = config['client']['client_id']
    client_secret = config['client']['client_secret']
    user_agent = config['client']['user_agent']
    
    global headers
    global redditheadertime
    
    headers = {'User-Agent':user_agent}
    data = {
        'grant_type':'password',
        'username': usern,
        'password': passw
           }
    
    auth = requests.auth.HTTPBasicAuth(client_id,client_secret)
    redditheadertime = utc_now()
    initres = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=data, headers=headers)
    TOKEN = initres.json()['access_token']
    headers['Authorization'] = f'bearer {TOKEN}'
    
    return headers



def reddit_condition_check(post):
    
    sins = ['pinned','stickied','over_18','is_video']
    for j in sins:
        
        if not int(post["data"][j]) == 0:
            return False
    return True



def reddit_media_check(post):
    imgext = ['jpg', 'jpeg', 'png', 'gif', 'bmp']
    vidext = ['mp4', 'avi', 'mov', 'flv', 'wmv']
    
    urlext = post['data']['url'].split('.')[-1].lower()
    
    if urlext in imgext:
        return 0
    elif urlext in vidext:
        return 1    
    else:
        return 2



def utc_now():
    
    utc_time = int(time.time())
    
    return utc_time




def reddit_data_capture(post, calltime):
    
    tempdata = []
    pdata = ['subreddit','title','upvote_ratio','ups','permalink','url','created_utc']
    pdata2 = ['subreddit','title','upvote_ratio','ups','permalink','url','created_utc','downloaded_utc']
    
    for j in pdata:
        tempdata.append(post['data'][j])

    tempdata.append(str(calltime))
    pdict = dict(zip(pdata2,tempdata))
    
    return pdict



def reddit_time_check(post):
    
    timedif = int(utc_now()) - int(post['data']['created_utc'])
    
    if timedif > 86400:
        return False
    else:
        return True

    
    
def get_post_data(subreddit, reqlimit):
    
    url = f"https://oauth.reddit.com/r/{subreddit}/hot.json?limit={reqlimit}"
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    
    return data



def token_check():
    
    tcheck = requests.get('https://oauth.reddit.com/api/v1/me', headers = headers).status_code
    
    if tcheck == 200:
        return True
    else:
        return False

    
    
def download_img(subreddit, post, postcount):
    
    main_dir = config['filepaths']['main_dir']

    placeholder = postcount-1
    subreddit_directory = os.path.join(main_dir, subreddit)
    
    if not os.path.exists(subreddit_directory):
        os.makedirs(subreddit_directory)
        
    response = requests.get(post['data']['url'], headers = headers)
    
    with open(os.path.join(subreddit_directory, f'{subreddit}_{placeholder}.jpg'), 'wb') as f:
        f.write(response.content)

        

def post_to_csv(df):
    
    csv_filepath = config['filepaths']['csv']
    
    if not os.path.isfile(csv_filepath): 
        try:
            df.to_csv(csv_filepath, index=False)
        except:
            print("file needs to be closed")    
    else:
        try:
            df.to_csv(csv_filepath, mode='a', header=False, index=False) 
        except:
            print("file needs to be closed")


            
def resolution_check(post):
    imgurl = post['data']['url']
    
    try:
        response = requests.get(imgurl, stream=True)
        img = Image.open(response.raw)
        width, height = img.size
        aspect = height/width
        
        if aspect > 1.7:
            return False
        else:
            return True
    except:
        return False


    

def var_init():
    
    try:
        redditheadertime
    except NameError:
        print("time since last header initialization: VAR NOT INITIALIZED")
    else:
        print("time since last header initialization: ", (utc_now()-redditheadertime), " seconds")
    
    try:
        redditfunctime
    except NameError:
        print("time since last function call: VAR NOT INITIALIZED")
    else:
        print("time since last function call: ", (utc_now()-redditfunctime), " seconds")


        

def reddit_submain(subreddit, reqlimit, limit, calltime):
    
    postdata = ['subreddit','title','upvote_ratio','ups','permalink','url','created_utc','downloaded_utc']
    data = get_post_data(subreddit,reqlimit)
    df = pd.DataFrame(columns=[x for x in postdata])
    postcount = 0
    rejectcount = 0
    
    for i, post in enumerate(data['data']['children']):
        if reddit_condition_check(post) == True and reddit_media_check(post) == 0 and reddit_time_check(post) == True and resolution_check(post) == True:
            postcount += 1
            new_data = pd.DataFrame.from_dict(reddit_data_capture(post, calltime), orient='index').T
            df = pd.concat([df, new_data], ignore_index=True)
            download_img(subreddit, post, postcount)
        else:
            rejectcount += 1

        if postcount == limit:
            break

    post_to_csv(df)
    print(df)
    
    if postcount != limit:
        print("Post count was only ",postcount)
    #df.tail()



def reddit_main(subreddit, reqlimit, limit):
    
    var_init()
    # 'headers' and 'redditheadertime' and 'redditfunctime' variables are GLOBAL - defined in header_init() and this function
    global redditfunctime
    calltime = utc_now()
    redditfunctime = utc_now()
    reddit_submain(subreddit,reqlimit,limit, calltime)