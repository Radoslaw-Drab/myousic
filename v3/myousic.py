from yt_dlp import YoutubeDL
from uuid import uuid4
from datetime import datetime
from tabulate import tabulate, SEPARATING_LINE
from types import SimpleNamespace
import urllib.parse, urllib.request
import pyperclip
import re
import requests

from track import TrackExtended
from utils.prompt import List, Input
from utils.system import clear
from utils.config import Config, SortType
import utils.colors as colors


cl = colors.Color()
itunesApiUrl = 'https://itunes.apple.com/search'

def main(*, url: str | None = None, search: str | None = None, download_only: bool = False):
  clear()
  id = uuid4()
  options = {
    'format': 'm4a/bestaudio/best', 
    'outtmpl': f'{id}.%(ext)s',
    'quiet': 'true',
  }
  config = Config()

  with YoutubeDL(options) as ydl:
    if download_only and url:
      track_download_only(ydl, id=id, url=url, config=config)
      end()
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
      print(cl.change(error, cl.text.RED))
      input()
      return
    # results: list[dict] = data['results']
    results: list[dict] = sorted(data['results'], key=lambda d: d[config.get_sort_key()], reverse=config.data.sort_type == SortType.DESC) if config.get_sort_key() != None else data['results']    


    if len(results) == 0:
      return main(search=search_menu(cl.change(f'No results found for ', cl.text.RED) + cl.change(term, cl.text.BLUE)))

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

    title = f"Select for {cl.change(term, cl.text.BLUE)}"
    options = sort_results(None, config.data.sort_type)
    index = List(options, title, sort_types=['title', 'artist', 'album', 'year'], sort_listener=sort_results, show_count=config.data.show_count).get_index() if len(options) > 1 else 0
    
    
    t = TrackExtended(results[index], id, config=config)

    if get_track(ydl, url, t):
      end()

def end():
  print(cl.change('Press enter to end', cl.text.GREY))
  input()
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
    ['Artwork', cl.change(t.get_artwork_url(), cl.options.URL) if t.get_artwork_url() else '-'],
    ['Lyrics', cl.change(t.get_lyrics_url(), cl.options.URL)],
    ['Genres', cl.change(t.get_genres_url(), cl.options.URL)]
  ]

  table = tabulate(data, tablefmt='simple')
  return table
def get_track(ydl: YoutubeDL, url: str | None, t: TrackExtended):

  valid_lyrics = t.check_lyrics()
  valid_genres = t.check_genres()
  table = get_table(t)
  before_screen = table

  if not valid_lyrics:
    before_screen += cl.change('\nCouldn\'t find lyrics', cl.text.RED)
  if not valid_genres:
    before_screen += cl.change('\nCouldn\'t find genres', cl.text.RED)

  id = List([
      { "id": "download", "name": "Download" } if url else None, 
      { "id": "download-bare", "name": "Download without data" } if url else None, 
      { "id": 'exit', "name": 'Exit' }
    ], before_screen=before_screen, horizontal=True, show_info=False).get_value()
  download = id == 'download' or id == 'download-bare'
  get_lyrics = id != 'download-lyrics'
  get_genres = id != 'download-genres'
  
  if id == 'exit':
    return False
  
  if url:
    fileInfo = SimpleNamespace(**ydl.extract_info(url, download=download))
    if download:
      t.assign_file(fileInfo.audio_ext)
    if download and id != 'download-bare':
      t.metadata(get_lyrics=get_lyrics, get_genres=get_genres)
    

  print(table)
  if download:
    print(cl.change('Downloaded', cl.text.GREEN))
    t.save()
  return True
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
  [artist, title] = Input(title, 'Artist: ', 'Title: ').start()
  return f'{artist} - {title}'
def init():
  clear()
  id = List([
    {"id": "search-download", "name": "Search and Download"}, 
    {"id": "search", "name": "Search"}, 
    {"id": "download", "name": "Download"}, 
    {"id": "exit", "name": "Exit"}
    ], ordered=False, show_info=False, title=cl.change('Myousic', cl.text.BLUE)).get_value()
  print(id)
  if id == 'download' or id == 'search-download':
    url = pyperclip.paste()
    if not re.match(r'https?:\/\/(youtu\.be)|(youtube\.com)\/.*', url):
      url = input('Youtube URL: ')
    main(url=url, download_only= id == 'download')
  elif id == 'search':
    term = search_menu()
    main(search=term)
  elif id == 'exit':
    return
  
if __name__ == "__main__":
  init()
