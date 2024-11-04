import json
import re
from types import SimpleNamespace
from pathlib import Path
from enum import Enum

class PrintConfig:
  print_max_artist_size: int
  print_max_track_size: int
  print_max_album_size: int
class Replacement(dict):
  title: dict[str, str]
  artist: dict[str, str]
class ReplacementProp(Enum):
  TITLE = 'title'
  ARTIST = 'artist'
class ReplacementType(Enum):
  LYRICS = 'lyrics_regex'
  GENRES = 'genres_regex'

class SortType(Enum):
  ASC = 'asc'
  DESC = 'desc'
class ConfigType(PrintConfig):
  class Sort(Enum):
    ARTIST = 'artist'
    TITLE = 'title'
    ALBUM = 'album'
    YEAR = 'year'

  temp_folder: str
  output_folder: str
  artwork_size: int
  sort: Sort
  sort_type: SortType
  excluded_genres: list[str]
  included_genres: list[str]
  replace_genres: dict[str, str]
  lyrics_regex: Replacement
  genres_regex: Replacement
  show_count: int

defaultConfigType: ConfigType = {
  "print_max_artist_size": 35,
  "print_max_track_size": 40,
  "print_max_album_size": 25,
  "temp_folder": 'tmp',
  "output_folder": "music",
  "artwork_size": 1000,
  "excluded_genres": [],
  "included_genres": [],
  "replace_genres": {},
  "lyrics_regex": {
    "artist": {},
    "title": {}
  },
  "genres_regex": {
    "artist": {},
    "title": {}
  },
  "sort": None,
  "sort_type": "asc",
  "show_count": 10
}


  
class Config:
  path: str = './'
  file: str = 'config.json'
  data: ConfigType
  json_data: dict[str, any]
  def __init__(self, path: str = './'):
    self.path = path
    path = Path(self.path, self.file)
    if not Path.exists(path):
      open(path, 'w').write(json.dumps(defaultConfigType))
    file = open(path, 'r')
    self.json_data = { **defaultConfigType, **json.loads(file.read()) }
    self.data = SimpleNamespace(**self.json_data)
    self.__keys = {}
  
  def modify_genres(self, prop: ReplacementProp, text: str):
    return self.__modify_by_regex(ReplacementType.GENRES, prop, text)
  def modify_lyrics(self, prop: ReplacementProp, text: str):
    return self.__modify_by_regex(ReplacementType.LYRICS, prop, text)
  def __modify_by_regex(self, type: ReplacementType, prop: ReplacementProp, text: str):
    newText = text
    replacement: Replacement = self.json_data.get(type.value)
    if replacement == None:
      return newText

    regExs: dict[str, str] | None = replacement.get(prop.value)

    if regExs == None or len(regExs.keys()) == 0:
      return newText
    
    for regEx in regExs.keys():
      newText = re.sub(regEx, regExs[regEx], newText)

    return newText
  def get_sort_key(self, key: str | None = None):
    sort = self.data.sort if key == None else key
    if sort == 'title':
      return 'trackName'
    elif sort == 'artist':
      return 'artistName'
    elif sort == 'year':
      return 'releaseDate'
    elif sort == 'album':
      return 'collectionName'
    return None
  def set_key(self, key: str, value: any):
    d = {}
    d[key] = value
    self.__keys.update(d)
    self.keys: Keys = SimpleNamespace(**self.__keys)
    
  def youtube_dl(self):
    id = self.keys.id
    if id == None:
      raise ValueError('No ID set')
    
    from yt_dlp import YoutubeDL
    options = {
      'format': 'm4a/bestaudio/best', 
      'outtmpl': f'{id}.%(ext)s',
      'quiet': 'true',
    }
    return YoutubeDL(options)
  
  
  
class Keys(dict):
  from uuid import UUID
  id: UUID | None
  itunes_api_url: str | None