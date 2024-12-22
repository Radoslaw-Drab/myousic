import re
from prompt_toolkit.clipboard.pyperclip import PyperclipClipboard


from utils import Exit
from utils.config import Config
from utils.prompt import clear, Input, Color


def search_menu(title: str | None = 'Search'):
  try:
    [artist, title] = Input(title, 'Artist: ', 'Title: ').start()
    return f'{artist} - {title}'
  except Exit:
    return None

def get_artist_track(config: Config, url: str) -> tuple[str, str]:
  ydl = config.youtube_dl()
  info = ydl.extract_info(url, download=False)

  artist: str = info.get('artist') or info.get('creator') or info.get('uploader')
  title: str = info.get('track') or info.get('fulltitle') or info.get('alt_title')


  formattedTitle = re.sub(' x ', ', ', re.sub('(\\[|\\().*(\\]|\\))', '', title))

  artist_match = re.match(r'.*(?= - )', formattedTitle)
  if artist_match and info.get('artist') != None:
    artist = artist_match.string

  formattedTitle = re.sub(f'{artist}.*- *', '', formattedTitle)

  title_split = formattedTitle.split('-')

  return (artist, formattedTitle) if re.search(artist.lower(), formattedTitle.lower()) != None or len(title_split) <= 1 else (title_split[0], *title_split[1:])
  
def get_info_term(config: Config, url: str):
  (artist, title) = get_artist_track(config, url)
  return f'{artist} - {title}'
def valid_url(url: str | None):
  return bool(re.match(r'https?:\/\/(youtu\.be)|(youtube\.com)\/.*', url or ''))
def input_url(config: Config) -> str | None: 
  try:
    clear()
    url = PyperclipClipboard().get_data().text or ''
    title = 'No URL'
    url_valid = valid_url(url)
    if url_valid:
      title = get_info_term(config, url)
      
    
    [url_input] = Input(
      Color.get_color('Youtube info: ', Color.GREY) + Color.get_color(title, Color.PRIMARY), 
      ('YouTube URL' + (f" ({Color.get_color('Enter', Color.SECONDARY)} for default)" if url_valid else '') + ': ', Color.get_color(url, Color.GREY) if url_valid else '')
    ).start()
    
    url = url_input if url_input != '' else url
    if not valid_url(url):
      return input_url(config)

    return url
  except Exit:
    pass
  return None