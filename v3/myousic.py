from yt_dlp import YoutubeDL
from uuid import uuid4
import urllib.parse
import pyperclip
import re
import json
import requests
import colors
import utils
import datetime
import pick
import keyboard

cl = colors.colors()
url = pyperclip.paste()
itunesApiUrl = 'https://itunes.apple.com/search'

if not re.match(r'https?:\/\/(youtu\.be)|(youtube\.com)\/.*', url):
  url = input('Youtube URL: ')

id = uuid4()
# https://youtu.be/4YZ7HpQG9YM?si=jqPi9Rxu7UzcteIa
options = {
  'format': 'm4a/bestaudio/best', 
  'outtmpl': f'{id}.%(ext)s',
  'quiet': 'true',
}
# yt = YouTube(url)
with YoutubeDL(options) as ydl:
  info = ydl.extract_info(url, download=False)

  artist: str = info.get('artist') or info.get('uploader')
  title: str = info.get('fulltitle') or info.get('alt_title')

  formattedTitle = re.sub('(\\[|\\().*(\\]|\\))', '', title)

  term = f'{artist} - {formattedTitle}' 

  query = {
    'term': term
  }
  q = urllib.parse.urlencode(query, doseq=True)

  response = requests.get(f'{itunesApiUrl}?{q}')
  data = response.json()
  results: dict[str, str] = data['results']

  def maxSize(prop: str):
    return max([len(result.get(prop) or '') for result in results]) if len(results) > 0 else 0
  maxArtistName = maxSize('artistName')
  maxTrackName = maxSize('trackName')
  maxCollectionName = maxSize('collectionName')

  options = [f'{d.get('artistName').ljust(maxArtistName)} | {d.get("trackName").ljust(maxTrackName)} | {d.get("collectionName").ljust(maxCollectionName)} | {datetime.datetime.strptime(d["releaseDate"], "%Y-%m-%dT%H:%M:%SZ").year}' for d in results]
  # utils.clear()
  title = f"Select for {term}"

  # test = pick.Picker(options, title, indicator='>')
  # test.start()
  # print(test)
  selected, index = pick.pick(options, title, indicator='>')


  result: dict[str, str] = results[index]
  for k in result:
    print(f"{k}: {result[k]}")

  input()

  # author = yt.author
  # title = yt.title

  # print(author, title, sep=' | ')
  # print(yt.streams.filter(only_audio=True))
  # yt.streams.filter(adaptive=True).first().download()

# print('Some videos failed to download' if error_code
#       else 'All videos successfully downloaded')