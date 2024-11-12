from pathlib import Path

from uuid import uuid4

from views.search import init as search
from views.download import init as download
from views.bare_download import init as bare_download

from utils import Exit
from utils.config import Config
from utils.views import search_menu, input_url
from utils.prompt import clear, List, get_color, ColorType

def init():
  clear()
  config = Config(Path.home())
  config.set_key('id', uuid4())
  config.set_key('itunes_api_url', 'https://itunes.apple.com/search')
  config.set_key('temp_folder', config.data.temp_folder)
  config.set_key('output_folder', config.data.output_folder)
  
  try:
    id = List([
      {"id": "search-download", "name": "Search and Download"}, 
      {"id": "search", "name": "Search"}, 
      {"id": "download", "name": "Download"}, 
      {"id": "exit", "name": "Exit"}
      ], 
      ordered=False, title=get_color('Myousic', ColorType.PRIMARY)).get_value()
    
    url: str | None = None
    
    if id == 'search-download' or id == 'download':
      url = input_url(config)
    
    if id == 'search':
      term = search_menu()
      track = search(term, config=config)
      if track != None:
        track.get_table(True)
    if id == 'search-download' and url:
      download(config, url)
    if id == 'download' and url:
      bare_download(config, url)
    if id == 'exit' or id == None:
      return
    init()
  except Exit:
    return
  
