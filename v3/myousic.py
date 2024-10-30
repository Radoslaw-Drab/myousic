from yt_dlp import YoutubeDL
from uuid import uuid4
from datetime import datetime
from tabulate import tabulate, SEPARATING_LINE
from types import SimpleNamespace
import urllib.parse, urllib.request
from pathlib import Path
import pyperclip
import re
import requests

from track import TrackExtended
from utils import Exit
from utils.prompt import List, Input, get_color, ColorType, print_color, print_formatted
from utils.system import clear
from utils.config import Config, SortType
import utils.colors as colors


cl = colors.Color()
itunesApiUrl = 'https://itunes.apple.com/search'

def youtube_dl():
  id = uuid4()
  options = {
    'format': 'm4a/bestaudio/best', 
    'outtmpl': f'{id}.%(ext)s',
    'quiet': 'true',
  }
  return YoutubeDL(options)
  
def main(*, url: str | None = None, search: str | None = None, download_only: bool = False):
  clear()
  config = Config(Path.home())
  ydl = youtube_dl()
  if download_only and url:
    try:
      track_download_only(ydl, id=id, url=url, config=config)
      end()
    except Exit: 
      pass
    return
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
    'term': term,
    'limit': 200,
    'entity': ['musicArtist', 'musicTrack', 'album', 'song']
  }
  q = urllib.parse.urlencode(query, doseq=True)

  response = requests.get(f'{itunesApiUrl}?{q}')
  data: dict = response.json()
  error = data.get('errorMessage')
  if error:
    print_color(error, ColorType.ERROR)
    input()
    return
  results: list[dict] = sorted(data['results'], key=lambda d: d[config.get_sort_key()], reverse=config.data.sort_type == SortType.DESC) if config.get_sort_key() != None else data['results']    


  if len(results) == 0:
    return main(search=search_menu(get_color('No results found for ', ColorType.ERROR) + get_color(term, ColorType.PRIMARY)))

  def maxSize(prop: str):
    return max(0, *[len(result.get(prop) or '') for result in results]) if len(results) > 0 else 0
  def get_date(date: str):
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
  maxArtistName = min(maxSize('artistName'), config.data.print_max_artist_size)
  maxTrackName = min(maxSize('trackName'), config.data.print_max_track_size)
  maxCollectionName = min(maxSize('collectionName'), config.data.print_max_album_size)

  def get_result(dictionary: dict, prop: str, max_size: int):
    return (dictionary.get(prop)[:max_size] if dictionary.get(prop) != None else '-').ljust(max_size)

  def sort_results(sort_by: str | None, sort_type: SortType = SortType.ASC):
    options: list[str] = []
    sorted_results = sorted(results, key=lambda d: d[config.get_sort_key(sort_by)], reverse=sort_type == SortType.DESC) if sort_by != None else results
    for r in sorted_results:
      artistName = get_result(r, 'artistName', maxArtistName)
      trackName = get_result(r, 'trackName', maxTrackName)
      collectionName = get_result(r, 'collectionName', maxCollectionName)
      year = get_date(r.get('releaseDate')).year if r.get('releaseDate') != None else '-'
      options.append(f'{trackName} | {artistName} | {collectionName} | {year}')
    return options

  title = f"Select for {get_color(term, ColorType.PRIMARY)}"
  options = sort_results(None, config.data.sort_type)
  try:
    index = List(options, title, sort_types=['title', 'artist', 'album', 'year'], sort_listener=sort_results, show_count=config.data.show_count).get_index() if len(options) > 1 else 0
    
    if index == None: return
    t = TrackExtended(results[index], id, config=config)

    if get_track(ydl, url, t):
      end()
  except Exit:
    return

def end():
  try:
    print_color('Press Enter to end', ColorType.GREY)
    input()
  except KeyboardInterrupt:
    raise Exit
def get_table(t: TrackExtended):
  t
  track = t.value
  date = t.get_date()
  data = [
    ['Track', track.trackName],
    ['Artist', track.artistName],
    ['Album', track.collectionName if track.collectionName else '-'],
    SEPARATING_LINE,
    ['Genre', track.primaryGenreName if track.primaryGenreName else '-'],
    ['Other Genres', t.get_genres_str()],
    ['Explicitness', track.collectionExplicitness if track.collectionExplicitness else '-'],
    SEPARATING_LINE,
    ['Date', date if type(date) is str else date.year],
    ['Track', f'{track.trackNumber} / {track.trackCount}' if track.trackNumber != None and track.trackCount != None else '-'],
    ['Disc', f'{track.discNumber} / {track.discCount}' if track.discNumber != None and track.discCount != None else '-'],
    SEPARATING_LINE,
    ['Artwork', get_color(t.get_artwork_url(), ColorType.PRIMARY) if t.get_artwork_url() else '-'],
    ['Lyrics', get_color(t.get_lyrics_url(), ColorType.PRIMARY)],
    ['Genres', get_color(t.get_genres_url(), ColorType.PRIMARY)]
  ]

  table = tabulate(data, tablefmt='plain')
  return table
def get_track(ydl: YoutubeDL, url: str | None, t: TrackExtended):
  valid_lyrics = t.check_lyrics()
  valid_genres = t.check_genres()
  table = get_table(t)
  before_screen = table

  if not valid_lyrics:
    before_screen += f'\n{get_color('Couldn\'t find lyrics', ColorType.ERROR)}'
  if not valid_genres:
    before_screen += f'\n{get_color('Couldn\'t find genres', ColorType.ERROR)}'
  
  clear()
  try:
    id = List([
        { "id": "download", "name": "Download" } if url else None, 
        { "id": "download-bare", "name": "Download without data" } if url else None, 
        { "id": 'exit', "name": 'Exit' }
      ], before_screen=before_screen, horizontal=True).get_value()
    download = id == 'download' or id == 'download-bare'
    get_lyrics = id != 'download-lyrics'
    get_genres = id != 'download-genres'
    
    if id == 'exit' or id == None:
      return False
    
    if url:
      fileInfo = SimpleNamespace(**ydl.extract_info(url, download=download))
      if download:
        t.assign_file(fileInfo.audio_ext)
      if download and id != 'download-bare':
        t.metadata(get_lyrics=get_lyrics, get_genres=get_genres)
      
    clear()
    print_formatted(table)
    if download:
      print_color('Downloaded', ColorType.SUCCESS)
      t.save()
    return True
  except Exit:
    return False
def track_download_only(ydl: YoutubeDL, *, id: str, url: str, config: Config):
  track = TrackExtended({}, id, config=config)
  
  track.get_missing({
    'artistName': 'Artist',
    'trackName': 'Title',
    'collectionName': 'Album',
    'releaseDate': 'Release Date',
    'primaryGenreName': 'Genre',
    'artworkUrl100': 'Artwork URL',
  })
  
  info = ydl.extract_info(url)
  track.assign_file(info.get('audio_ext'))
  track.metadata()

  print(get_table(track))
  track.save()
 

def search_menu(title: str | None = 'Search'):
  try:
    [artist, title] = Input(title, 'Artist: ', 'Title: ').start()
    return f'{artist} - {title}'
  except Exit:
    return None
def valid_url(url: str | None):
  return bool(re.match(r'https?:\/\/(youtu\.be)|(youtube\.com)\/.*', url))
def input_url(): 
  try:
    clear()
    url = pyperclip.paste()
    title = 'No URL'
    if valid_url(url):
      info = youtube_dl().extract_info(url, download=False)
      title = (info.get('track') or info.get('fulltitle')) + ' / ' + (info.get('artist') or info.get('uploader'))
    [url_input] = Input(get_color('Youtube info: ', ColorType.GREY) + get_color(title, ColorType.SECONDARY), 'YouTube URL' + (' (Enter for clipboard)' if valid_url(url) else '') + ': ').start()
    url = url_input if url_input != '' else url
    if not valid_url(url):
      return input_url()

    return url
  except Exit:
    pass
  return None
def init():
  clear()
  try:
    id = List([
      {"id": "search-download", "name": "Search and Download"}, 
      {"id": "search", "name": "Search"}, 
      {"id": "download", "name": "Download"}, 
      {"id": "exit", "name": "Exit"}
      ], ordered=False, title=get_color('Myousic', ColorType.PRIMARY)).get_value()
    if id == 'download' or id == 'search-download':
      url = input_url()
      if url != None:
        main(url=url, download_only= id == 'download')
    elif id == 'search':
      term = search_menu()
      if term != None:
        main(search=term)
    if id == 'exit' or id == None:
      return
    
    init()
  except Exit:
    return
  
if __name__ == "__main__":
  init()
