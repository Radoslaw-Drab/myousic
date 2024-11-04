import re
from datetime import datetime

from track import TrackExtended
from utils import Exit
from utils.prompt import get_color, ColorType
from utils.views import get_artist_track
from utils.config import Config

def init(config: Config, url: str):
  id = config.keys.id
  ydl = config.youtube_dl()
  track = TrackExtended({}, id, config=config)
  
  (artist, title) = get_artist_track(config, url)
  info = ydl.extract_info(url, download=False)
    
  date = info.get('upload_date')
  if date != None and re.match(r'\d{4}\d{2}\d{2}', date):
    date = str(datetime.strptime(info.get('upload_date'), '%Y%m%d').year)
  
  def placeholder(text: str):
    return get_color(text, ColorType.GREY)
  try:
    track.get_missing({
      'artistName': ('Artist', placeholder(artist)),
      'trackName': ('Title', placeholder(title)),
      'collectionName': ('Album', placeholder(title + ' - Single')),
      'releaseDate': ('Release Date', placeholder(date)),
      'primaryGenreName': 'Genre',
      'artworkUrl100': ('Artwork URL', placeholder(info.get('thumbnail'))),
    })
    ydl.download(url)
    
    track.assign_file(info.get('audio_ext'))
    track.metadata()

    # print(get_table(track))
    track.get_table(True)
    track.save()
  except Exit:
    return