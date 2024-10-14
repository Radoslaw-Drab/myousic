from yt_dlp import YoutubeDL
from uuid import uuid4
from datetime import datetime
from tabulate import tabulate, SEPARATING_LINE
from types import SimpleNamespace
from itunes import Track
from utils import List
import urllib.parse
import pyperclip
import re
import requests
import colors
import os
from config import Config
import music_tag

cl = colors.Color()
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
config = Config()

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
  results: dict[str, dict] = data['results']

  def maxSize(prop: str):
    return max([len(result.get(prop) or '') for result in results]) if len(results) > 0 else 0
  def getDate(date: str):
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
  maxArtistName = min(maxSize('artistName'), config.data.print_max_artist_size)
  maxTrackName = min(maxSize('trackName'), config.data.print_max_track_size)
  maxCollectionName = min(maxSize('collectionName'), config.data.print_max_album_size)
  
  test: str = ''
  options = [f'{d.get('artistName')[:maxArtistName].ljust(maxArtistName)} | {d.get("trackName")[:maxTrackName].ljust(maxTrackName)} | {d.get("collectionName")[:maxCollectionName].ljust(maxCollectionName)} | {getDate(d["releaseDate"]).year}' for d in results]
  title = f"Select for {term}"

  index = List(options, title).getIndex()
  print(maxArtistName, maxTrackName, maxCollectionName, os.get_terminal_size().columns)

  result = results[index]
  track: Track = SimpleNamespace(**results[index])

  data = [
    ['Track', track.trackName],
    ['Artist', track.artistName],
    ['Album', track.collectionName],
    SEPARATING_LINE,
    ['Genre', track.primaryGenreName],
    ['Explicitness', track.collectionExplicitness],
    SEPARATING_LINE,
    ['Date', getDate(track.releaseDate).year],
    ['Track', f'{track.trackNumber} / {track.trackCount}'],
    ['Disc', f'{track.discNumber} / {track.discCount}'],
    SEPARATING_LINE,
    ['Artwork', re.sub('100x100', '1000x1000', track.artworkUrl100)]
  ]
  input()
  table = tabulate(data, ["Property", "Value"], tablefmt='simple')

  index = List(["Download", "Search lyrics"], "Action", beforeScreen=table, horizontal=True).getIndex()
  fileInfo = SimpleNamespace(**ydl.extract_info(url))
  # print(fileInfo.audio_ext)
  # input('Wait')


  # file = music_tag.load_file(f'{id}.{fileInfo.audio_ext}')
  # print(file.values)
  # file['title'] = track.trackName
  # file['author'] = track.artistName

  # print(author, title, sep=' | ')
  # print(yt.streams.filter(only_audio=True))
  # yt.streams.filter(adaptive=True).first().download()

# print('Some videos failed to download' if error_code
#       else 'All videos successfully downloaded')


