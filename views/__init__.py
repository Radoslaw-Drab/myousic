from pathlib import Path

from uuid import uuid4

from views.search import init as search
from views.download import init as download
from views.bare_download import init as bare_download
from views.settings import init as settings

from utils.config import Config
from utils.args import Args
from utils.views import search_menu, input_url
from utils.prompt import clear, List, Color
from utils import Exit

def init():
  clear()
  args = Args()
  config = Config(Path(args.config_path))
  config.set_key('id', uuid4())
  config.set_key('temp_folder', config.data.temp_folder)
  config.set_key('output_folder', config.data.output_folder)
  
  try:
    id = List([
      {"id": "search-download", "name": "Search and Download"}, 
      {"id": "search", "name": "Search"}, 
      {"id": "download", "name": "Download"}, 
      # {"id": "settings", "name": "Settings"}, 
      {"id": "exit", "name": "Exit"}
    ], 
    ordered=False, title=Color.get_color('Myousic', Color.PRIMARY)).get_value()
    
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
    if id == 'settings':
      settings(config)
    if id == 'exit' or id == None:
      return
    init()
  except Exit:
    return
  
