import urllib
import requests
from datetime import datetime

from track import TrackExtended
from utils import Exit
from utils.config import Config, SortType
from utils.views import search_menu
from utils.prompt import clear, List, get_color, print_color, ColorType


def init(search: str | None, *, config: Config) -> TrackExtended | None:
  clear()
  
  if search == None:
    return
  
  id = config.keys.id
  itunes_api_url = config.keys.itunes_api_url

  query = {
    'term': search,
    'limit': 200,
    'entity': ['musicArtist', 'musicTrack', 'album', 'song']
  }
  q = urllib.parse.urlencode(query, doseq=True)

  response = requests.get(f'{itunes_api_url}?{q}')
  if not response.ok:
    print_color(response.reason, ColorType.ERROR)
    input()
    return
  data: dict = response.json()
  
  error = data.get('errorMessage')
  if error:
    print_color(error, ColorType.ERROR)
    input()
    return
  
  results: list[dict] = sorted(data['results'], key=lambda d: d[config.get_sort_key()], reverse=config.data.sort_type == SortType.DESC) if config.get_sort_key() != None else data['results']    


  if len(results) == 0:
    try:
      return init(search=search_menu(get_color('No results found for ', ColorType.ERROR) + get_color(search, ColorType.PRIMARY)), config=config)
    except Exit:
      return None
  elif len(results) == 1:

  def get_date(date: str):
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
  
  def sort_results(sort_by: str | None, sort_type: SortType = SortType.ASC):
    from tabulate import tabulate
    ids: list[int] = []
    data: list[dict] = []
    sorted_results = sorted(results, key=lambda d: d[config.get_sort_key(sort_by)], reverse=sort_type == SortType.DESC) if sort_by != None else results

    for index in range(len(sorted_results)):
      r = sorted_results[index]
      year = get_date(r.get('releaseDate')).year if r.get('releaseDate') != None else '-'
      ids.append(sorted_results[index].get('trackId'))
      data.append({
        'index': index + 1,
        'artistName': r.get('artistName'),
        'trackName': r.get('trackName'),
        'collectionName': r.get('collectionName'),
        'year': year
      })
    table = tabulate([[value for value in d.values()] for d in data], tablefmt='presto')
    lines = table.split('\n')
    return [{"id": ids[index], "name": lines[index]} for index in range(len(lines))]

  title = f"Select for {get_color(search, ColorType.PRIMARY)}"
  options = sort_results(None, SortType.ASC)
  
  try:
    index = List(
      options, 
      title, 
      sort_types=['title', 'artist', 'album', 'year'], 
      sort_listener=sort_results, 
      show_count=config.data.show_count,   
      list_prefix=False          
    ).get_value() if len(options) > 1 else 0
    
    if index == None: return
    result = {}
    
    for data in results:
      if data.get('trackId') != index:
        continue
      result = data
      
    return TrackExtended(result, id, config=config)
  except Exit:
    return