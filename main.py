import re, json, os
from requests_html import HTMLSession, HTML
import urllib
from datetime import datetime
# from selenium import webdriver
import time
import pickle

# from selenium.webdriver.chrome.options import Options

headers = {'Accept': 'application/json, text/javascript, */*; q=0.01', 'Referer': 'https://www.twitch.tv/directory',
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8',
           'X-Device-Id': 'e510d6181102f37b',
           'Client-Id': 'kimne78kx3ncx6brgo4mv6wki5h1ko'}

cursors = set()
done = []
session = HTMLSession()


def save_json(id, title, publishedAt, lengthSeconds):
    obj = {'data': []}
    obj['data'].append({'id': id})
    obj['data'].append({'title': title})
    obj['data'].append({'time': publishedAt})
    obj['data'].append({'duration': lengthSeconds / 60})
    obj['data'].append({'url': 'https://www.twitch.tv/videos/' + str(id)})
    # print(obj)
    with open(str(id) + '.json', 'w') as outfile:
        json.dump(obj, outfile)
    os.rename(str(id) + '.json', paths + "/" + str(id) + '.json')
    print("{} Saved".format(id))


def save_thumbnail(id, previewThumbnailURL):
    if not os.path.exists(paths + "/" + str(id) + '.jpg'):
        urllib.request.urlretrieve(previewThumbnailURL, str(id) + ".jpg")
        os.rename(str(id) + ".jpg", paths + "/" + str(id) + ".jpg")


def get_data(cursor,gname):
    if cursor not in done:
        print("Cursor Value:--->"+cursor)
        payload = {"operationName": "DirectoryVideos_Game",
                   "variables": {"gameName":gname , "videoLimit": 30, "languages": [], "videoSort": "VIEWS",
                                 "followedCursor":cursor}, "extensions": {"persistedQuery": {"version": 1,
                                                                                              "sha256Hash": "c1aad1377690d68d6963cfcad6957320d76f0d3c325f42e267e0683da1a769c0"}}}

        url1 = "https://gql.twitch.tv/gql"
        r1 = session.post(url1, headers=headers, data=json.dumps(payload))
        html1 = r1.json()
        # print(html1)
        if 'errors' in html1:
            print("Error")
        else:
            # print(html1)
            try:
                game = html1["data"]['game']["name"]
            except:
                game = ""
            for i in html1["data"]['game']['videos']["edges"]:
                try:
                    id = i["node"]["id"]
                except:
                    id = ""
                if os.path.exists( paths + "/" + str(id) + ".json"):
                  print("Skipping (already there) -> " + id)
                else:
                  try:
                      lengthSeconds = i["node"]["lengthSeconds"]
                  except:
                      lengthSeconds = ""
                  try:
                      previewThumbnailURL = i["node"]["previewThumbnailURL"]
                  except:
                      previewThumbnailURL = ""
                  try:
                      publishedAt = i["node"]["publishedAt"]
                  except:
                      publishedAt = ""
                  try:
                      title = game+ " - " + i["node"]["title"]
                  except:
                      title = game

                  save_json(id, title, publishedAt, lengthSeconds)
                  try:
                      save_thumbnail(id, previewThumbnailURL)
                  except:
                      pass


paths = "Twitch"
if not os.path.exists(paths):
  os.makedirs(paths)
with open('new_urls.pkl', 'rb') as f:
  mynewlist = pickle.load(f)
with open('all_games.pkl', 'rb') as f:
  mygames = pickle.load(f)
for gm in mygames:
  print("Game:------------------->"+gm)
  for k in mynewlist:
    try:
      get_data(k,gm)
    except Exception as e:
      pass
      #print(e)

