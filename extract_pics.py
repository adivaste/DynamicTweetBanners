import os
import time
import requests
import tweepy
from PIL import Image, ImageDraw
from dotenv import load_dotenv

# Loading Environment variables
load_dotenv()

# Scraping Limit (in Seconds)
CURR_SCRAPE_LIMIT = 60
HIGH_SCRAPE_LIMIT = 120
SCRAPE_LIMIT = CURR_SCRAPE_LIMIT

# API Keys and Access Tokens 
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_SECRET = os.getenv('ACCESS_SECRET')


# Authenticate to Twitter 
auth  = tweepy.OAuthHandler(API_KEY,API_SECRET)
auth.set_access_token(ACCESS_TOKEN,ACCESS_SECRET)
api = tweepy.API(auth)


# Checking the Provided data is valid or not
try:
    api.verify_credentials()
    print("[ TWITTER ] : Authentication Successfull ")
except:
    print("[ TWITTER ] : Authentication Unsuccessfull due to Invalid Credential Details ! ")

#------------------------ F U N C T I O N S ----------------------------

# Make a copy of the default profile picture
def makeCopyOfFile(original,target):
    with open(original,"rb") as ef:
        data = ef.read()
        with open(target,"wb") as nf:
            nf.write(data)


# Delete Extracted Profile Pictures
def deleteProfilePictures():
    for i in range(5):
        os.remove(f"{i+1}.png")


# Extracting Profile Pictures from Twitter 
def extractProfilePictures(username=None):

    # Getting Twitter User Info
    global SCRAPE_LIMIT
    try:
        user = api.get_user(screen_name = ( username or "imvkohli"))
        SCRAPE_LIMIT = CURR_SCRAPE_LIMIT
    except:
        print(f"[ TWITTER ] : API Limit Exceeded or Internal Server Error !")
        print(f"[ TWITTER ] : Trying in {SCRAPE_LIMIT} Seconds !")
        SCRAPE_LIMIT = HIGH_SCRAPE_LIMIT
        return 0

    # Extracting the followers and their Profile Pictures
    recent_count = 0
    try:
        followers = user.followers()[:5]
        SCRAPE_LIMIT = CURR_SCRAPE_LIMIT
    except:
        followers = []
        SCRAPE_LIMIT = HIGH_SCRAPE_LIMIT
        print(f"[ TWITTER ] : API Requests Limit Exceeded or Server Error, Trying in {SCRAPE_LIMIT} Seconds !")
        return 0

    for follower in followers:
        recent_count += 1
        profile_image_url = follower.profile_image_url
        profile_image_url = profile_image_url.replace("normal","400x400")

        try:
            response = requests.get(profile_image_url)
            if (response.status_code == 200):
                with open(f"./images/{recent_count}.png", "wb") as f:
                    f.write(response.content)
            else:
                print(f"[ TWITTER ] : Error While Downloading Profile Pic. for @{follower.screen_name}")
                try:
                    makeCopyOfFile("./default_pic.png",f"./images/{recent_count}.png")   # Copy of the file (original,target)
                    print(f"[ TWITTER ] : Assigned the Default Profile Picture for @{follower.screen_name}")
                except:
                    print(f"[ TWITTER ] : Error In Creating Default Profile Pic !")
        except:
            print(f"[ TWITTER ] : Error In Getting the Correct Profile Picture URL !")
    print("[ TWITTER ] : All Profile Pictures Scraped Perfectly !")
    return 1


# Create the mask for rounded profile picture on header 
def createMask(im):
    mask_im = Image.new("L", im.size, 0)
    draw = ImageDraw.Draw(mask_im)
    draw.ellipse((0,0,140,140), fill=255)
    return mask_im

# Pasting the profile pictures on header's background 
def createHeaderImage():
    background = Image.open('background.png')
    profile_images = []

    header = background.copy()

    for i in range(1,6):
        try:
            img = Image.open(f"./images/{i}.png").resize((140,140))
            profile_images.append(img)
        except:
            print(f"[ PILLOW  ] : Error While Loading the Profile Pic {i}")

    print("[ PILLOW  ] : Resizing of Profile Pictures Done Properly.")

    header.paste(profile_images[0],(313,172),createMask(profile_images[0]))
    header.paste(profile_images[1],(499,172),createMask(profile_images[1]))
    header.paste(profile_images[2],(688,172),createMask(profile_images[2]))
    header.paste(profile_images[3],(874,172),createMask(profile_images[3]))
    header.paste(profile_images[4],(1049,172),createMask(profile_images[4]))
    header.save('./images/header.png', quality=100)
    print("[ PILLOW  ] : Your Header Saved as 'header.png' in 'images' Directory Successfully !!")

while True:
    if extractProfilePictures():
        createHeaderImage()
        SCRAPE_LIMIT = CURR_SCRAPE_LIMIT
    print(f"[  SLEEP  ] : Time Sleep of {SCRAPE_LIMIT} Seconds")
    time.sleep(SCRAPE_LIMIT)
