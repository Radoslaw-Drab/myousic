import json
import re
from types import SimpleNamespace
from pathlib import Path
from enum import Enum

class Modifier(dict):
  title: dict[str, str]
  artist: dict[str, str]
class ModifierProp(Enum):
  TITLE = 'title'
  ARTIST = 'artist'
class ModifierType(Enum):
  LYRICS = 'lyrics_url_modifiers'
  GENRES = 'genres_url_modifiers'

class SortType(Enum):
  ASC = 'asc'
  DESC = 'desc'
class ConfigType():
  class Sort(Enum):
    ARTIST = 'artist'
    TITLE = 'title'
    ALBUM = 'album'
    YEAR = 'year'

  temp_folder: str
  output_folder: str
  artwork_size: int
  excluded_genres: list[str]
  included_genres: list[str]
  genres_modifiers: dict[str, str]
  lyrics_modifiers: dict[str, str]
  lyrics_url_modifiers: Modifier
  genres_url_modifiers: Modifier
  show_count: int

default_config_type: ConfigType = {
  "temp_folder": str(Path.joinpath(Path.home(), 'tmp')),
  "output_folder": str(Path.joinpath(Path.home(), "music")),
  "artwork_size": 1000,
  "excluded_genres": [],
  "included_genres": [],
  "genres_modifiers": {},
  "lyrics_modifiers": {},
  "lyrics_url_modifiers": {
    "artist": {},
    "title": {}
  },
  "genres_url_modifiers": {
    "artist": {},
    "title": {}
  },
  "show_count": 10
}


  
class Config:
  file: str = 'config.json'
  def __init__(self, path: str = './'):
    self.path = Path(path, self.file)
    self.get_data()
    self.__keys = {}
    self.default_config_type: dict = default_config_type
  
  def modify_genres(self, prop: ModifierProp, text: str):
    return self.__modify_by_regex(ModifierType.GENRES, prop, text)
  def modify_lyrics(self, prop: ModifierProp, text: str):
    return self.__modify_by_regex(ModifierType.LYRICS, prop, text)
  def get_data(self):
    self.data: ConfigType = SimpleNamespace(**self.get_data_json())
    return self.data
  def set_data(self, key: str, value: any):
    d = self.get_data_json()
    obj = {}
    obj[key] = value
    with open(self.path, 'w') as file:
      file.write(json.dumps({ **d, **obj }))
    self.get_data()
    
  def get_data_json(self):
    if not Path.exists(self.path):
      with open(self.path, 'w') as file:
        file.write(json.dumps(default_config_type))
    
    with open(self.path) as file:
      self.json_data = { **default_config_type, **json.loads(file.read()) }
    return self.json_data
  def __modify_by_regex(self, type: ModifierType, prop: ModifierProp, text: str):
    newText = text
    modifier: Modifier = self.json_data.get(type.value)
    if modifier == None:
      return newText

    regExs: dict[str, str] | None = modifier.get(prop.value)

    if regExs == None or len(regExs.keys()) == 0:
      return newText
    
    for regEx in regExs.keys():
      newText = re.sub(regEx, regExs[regEx], newText)

    return newText
  def get_sort_key(self, key: str | None = None):
    if key == 'title':
      return 'trackName'
    elif key == 'artist':
      return 'artistName'
    elif key == 'year':
      return 'releaseDate'
    elif key == 'album':
      return 'collectionName'
    return None
  def set_key(self, key: str, value: any):
    d = {}
    d[key] = value
    self.__keys.update(d)
    self.keys: Keys = SimpleNamespace(**self.__keys)
    
  def youtube_dl(self):
    id = self.keys.id
    temp_folder = self.keys.temp_folder
    

    if id == None:
      raise ValueError('No ID set')
    
    from yt_dlp import YoutubeDL
    options = {
      'format': 'm4a/bestaudio/best', 
      'outtmpl': f'{id}.%(ext)s',
      'quiet': 'true',
      'progress': 'true',
      'paths': { 
        "temp": temp_folder or './', 
        "home": temp_folder or './'
      }
    }
    return YoutubeDL(options)
  
  
  
class Keys(dict):
  from uuid import UUID
  id: UUID | None
  itunes_api_url: str | None
  temp_folder: str | None
  output_folder: str | None