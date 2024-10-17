from yt_dlp import YoutubeDL
from uuid import uuid4
from datetime import datetime
from tabulate import tabulate, SEPARATING_LINE
from types import SimpleNamespace
import urllib.parse, urllib.request
import pyperclip
import re
import requests
import keyboard

from track import TrackExtended
from utils.prompt import List
from utils.system import clear
from utils.config import Config, SortType
import utils.colors as colors


cl = colors.Color()
url = pyperclip.paste()
itunesApiUrl = 'https://itunes.apple.com/search'

if not re.match(r'https?:\/\/(youtu\.be)|(youtube\.com)\/.*', url):
  url = input('Youtube URL: ')


def main(search: str | None = None):
  clear()
  global url, cl, itunesApiUrl
  id = uuid4()
  options = {
    'format': 'm4a/bestaudio/best', 
    'outtmpl': f'{id}.%(ext)s',
    'quiet': 'true',
  }
  config = Config()

  with YoutubeDL(options) as ydl:
    if search == None:
      info = ydl.extract_info(url, download=False)

      artist: str = info.get('artist') or info.get('uploader')
      title: str = info.get('track') or info.get('fulltitle') or info.get('alt_title')


      formattedTitle = re.sub(' x ', ', ', re.sub('(\\[|\\().*(\\]|\\))', '', title))

      artist_match = re.match(r'.*(?= - )', formattedTitle)

      if artist_match and info.get('artist') != None:
        artist = artist_match.string


      term = f'{artist} - {formattedTitle}' if re.search(artist, formattedTitle) == None else formattedTitle
    else:
      term = search

    query = {
      'term': term
    }
    q = urllib.parse.urlencode(query, doseq=True)

    response = requests.get(f'{itunesApiUrl}?{q}')
    data = response.json()
    # results: list[dict] = data['results']
    results: list[dict] = sorted(data['results'], key=lambda d: d[config.get_sort_key()], reverse=config.data.sort_type == SortType.DESC) if config.get_sort_key() != None else data['results']
    


    if len(results) == 0:
      print(cl.change(f'No results found for', cl.text.RED), cl.change(term, cl.text.BLUE))
      artist = input('Artist: ')
      title = input('Title: ')
      return main(f'{artist} - {title}')

    def maxSize(prop: str):
      return max([len(result.get(prop) or '') for result in results]) if len(results) > 0 else 0
    def get_date(date: str):
      return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
    maxArtistName = min(maxSize('artistName'), config.data.print_max_artist_size)
    maxTrackName = min(maxSize('trackName'), config.data.print_max_track_size)
    maxCollectionName = min(maxSize('collectionName'), config.data.print_max_album_size)

    
    options: list[str] = []

    def get_result(dictionary: dict, prop: str, max_size: int):
      return (dictionary.get(prop)[:max_size] if dictionary.get(prop) != None else '-').ljust(max_size)

    for r in results:
      artistName = get_result(r, 'artistName', maxArtistName)
      trackName = get_result(r, 'trackName', maxTrackName)
      collectionName = get_result(r, 'collectionName', maxCollectionName)
      year = get_date(r.get('releaseDate')).year if r.get('releaseDate') != None else '-'
      options.append(f'{artistName} | {trackName} | {collectionName} | {year}')

    title = f"Select for {term} ({len(options)})"


    index = List(options, title).get_index() if len(options) > 1 else 0

    t = TrackExtended(SimpleNamespace(**results[index]), id, config=config)
    track = t.value

    data = [
      ['Track', track.trackName],
      ['Artist', track.artistName],
      ['Album', track.collectionName],
      SEPARATING_LINE,
      ['Genre', track.primaryGenreName],
      ['Other Genres', t.get_genres_str()],
      ['Explicitness', track.collectionExplicitness],
      SEPARATING_LINE,
      ['Date', t.get_date().year],
      ['Track', f'{track.trackNumber} / {track.trackCount}'],
      ['Disc', f'{track.discNumber} / {track.discCount}'],
      SEPARATING_LINE,
      ['Artwork', t.get_artwork_url()],
      ['Lyrics', t.get_lyrics_url()],
      ['Genres', t.get_genres_url()]
    ]

    table = tabulate(data, tablefmt='simple')

    id = List([
        { "id": "download", "name": "Download" }, 
        { "id": "download-bare", "name": "Download without data" }, 
        # { "id": "download-lyrics", "name": "Download without lyrics" }, 
        # { "id": "download-genres", "name": "Download without genres" }, 
        { "id": 'exit', "name": 'Exit' }
      ], beforeScreen=table, horizontal=True).get_value()
    download = id != 'exit'
    get_lyrics = id != 'download-lyrics'
    get_genres = id != 'download-genres'
    
    fileInfo = SimpleNamespace(**ydl.extract_info(url, download=download))
    t.assign_file(fileInfo.audio_ext)
    if download and id != 'download-bare':
      t.metadata(get_lyrics=get_lyrics, get_genres=get_genres)
     

    print(table)
    print(cl.change('Downloaded', cl.text.GREEN))
    print(cl.change('Press enter to end', cl.text.GREY))
    keyboard.wait('enter')

    t.save()

main()