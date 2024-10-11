from yt_dlp import YoutubeDL
import pyperclip
import re
import json
import requests

url = pyperclip.paste()
itunesApiUrl = 'https://itunes.apple.com/search?'

if not re.match(r'https?:\/\/(youtu\.be)|(youtube\.com)\/.*', url):
  url = input('Youtube URL: ')

# yt = YouTube(url)
ydl = YoutubeDL({'format': 'm4a/bestaudio/best'})

if ydl:
  info = ydl.extract_info(url, download=False)

  artist = info['artist'] or info['uploader']
  title = info['fulltitle'] or info['alt_title']

  # i = json.dumps(ydl.sanitize_info(info))

  print(artist, title)
  # author = yt.author
  # title = yt.title

  # print(author, title, sep=' | ')
  # print(yt.streams.filter(only_audio=True))
  # yt.streams.filter(adaptive=True).first().download()
