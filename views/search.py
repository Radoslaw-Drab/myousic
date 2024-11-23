import urllib
import requests
from datetime import datetime
import re

from track import TrackExtended
from utils import Exit
from utils.config import Config, SortType
from utils.views import search_menu
from utils.prompt import List, Color, clear


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
    Color.print_color(response.reason, Color.ERROR)
    input()
    return
  data: dict = response.json()
  
  error = data.get('errorMessage')
  if error:
    Color.print_color(error, Color.ERROR)
    input()
    return
  
  results: list[dict] = sorted(data['results'], key=lambda d: d[config.get_sort_key()], reverse=config.data.sort_type == SortType.DESC) if config.get_sort_key() != None else data['results']    

  if len(results) == 0:
    try:
      return init(search=search_menu(Color.get_color('No results found for ', Color.ERROR) + Color.get_color(search, Color.PRIMARY)), config=config)
    except Exit:
      return None
  elif len(results) == 1:
    return TrackExtended(results[0], id, config)

  def get_date(date: str):
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
  
  def sort_results(sort_by: str | None, sort_type: SortType = SortType.ASC):
    from tabulate import tabulate
    data: list[dict[str, int | dict]] = []
    sorted_results = sorted(results, key=lambda d: d[config.get_sort_key(sort_by)], reverse=sort_type == SortType.DESC) if sort_by != None else results

    for index in range(len(sorted_results)):
      r = sorted_results[index]
      year = get_date(r.get('releaseDate')).year if r.get('releaseDate') != None else '-'
      data.append({
        'id': r.get('trackId'),
        'values': {
          'index': index + 1,
          'artistName': r.get('artistName'),
          'trackName': r.get('trackName'),
          'collectionName': r.get('collectionName'),
          'year': year
        }
      })
    table = tabulate([[value for value in d.get('values').values()] for d in data], tablefmt='presto', maxcolwidths=[None, 30, 30, 20, None])
    lines = re.split(r'\n(?=^ *\d+)', table, flags=re.MULTILINE)
    return [{"id": str(data[index].get('id')), "name": lines[index]} for index in range(len(lines))]

  title = f"Select for {Color.get_color(search, Color.PRIMARY)}"
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
    result: dict | None = None
    for data in results:
      if str(data.get('trackId')) != index:
        continue
      result = data
    if result == None:
      raise ValueError(f'Invalid {index} index')

    return TrackExtended(result, id, config=config)
  except Exit:
    return