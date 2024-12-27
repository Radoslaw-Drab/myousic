import json
import re
from pathlib import Path

from utils.classes import Obj
from type.Config import AppConfig, UrlModifier

  
class Config:
  AppConfig = AppConfig
  def __init__(self, path: Path = Path(Path.home(), 'myousic.json')):
    self.path = path
    self.data = AppConfig()
    self.keys = AppConfig.Keys()
    self.get_data()
  
  def update_config(self, config: AppConfig | None = None) -> None:
    with open(self.path, 'w') as file:
      file.write(config.json() if config else self.data.json())
  def __get_config(self) -> AppConfig:
    with open(self.path) as file:
      json_data = json.loads(file.read())
      app_config = AppConfig()
      for json_prop in json_data:
        setattr(app_config, json_prop, json_data[json_prop])
      return app_config

  def set_data[T](self, key: str, value: T):
    if key not in Obj.get_attributes(self.data):
      raise ValueError(f'Key not found: {key}')
    
    setattr(self.data, key, value)
    self.update_config()
  def get_data(self) -> AppConfig:
    if not Path.exists(self.path):
      self.update_config(AppConfig())
    
    self.data = self.__get_config()
    return self.data
  
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
  def set_key[T](self, key: str, value: T):
    setattr(self.keys, key, value)
  
  def modify_genres(self, key: UrlModifier.Key, text: str):
    return self.__modify_by_regex(UrlModifier.Prop.GENRES, key, text)
  def modify_lyrics(self, key: UrlModifier.Key, text: str):
    return self.__modify_by_regex(UrlModifier.Prop.LYRICS, key, text)
  def __modify_by_regex(self, type: UrlModifier.Prop, key: UrlModifier.Key, text: str):
    new_text = text
    modifier: UrlModifier = getattr(self.data, type.value)
    if modifier is None:
      return new_text

    reg_exs: dict[str, str] | None = modifier.get(key.value)

    if reg_exs is None or len(reg_exs.keys()) == 0:
      return new_text
    
    for reg_ex in reg_exs.keys():
      new_text = re.sub(reg_ex, reg_exs[reg_ex], new_text)

    return new_text
    
  def youtube_dl(self):
    id = self.keys.id
    temp_folder = self.keys.temp_folder
    

    if id is None:
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