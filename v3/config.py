from types import SimpleNamespace
import json
import pathlib

class PrintConfig:
  print_max_artist_size: int
  print_max_track_size: int
  print_max_album_size: int
class ConfigType(PrintConfig):
  download: bool
  
class Config:
  path: str = './'
  file: str = 'config.json'
  data: ConfigType
  def __init__(self, path: str = './'):
    self.path = path
    file = open(pathlib.Path(self.path, self.file), 'r')
    self.data = SimpleNamespace(**json.loads(file.read()))
    pass