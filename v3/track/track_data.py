import requests
import re
import urllib.parse
from bs4 import BeautifulSoup

from utils.text import uppercase

class Lyrics:
  def __init__(self, lyrics_url: str = 'https://lyrist.vercel.app/api'):
    self.lyrics_url = lyrics_url
    self.lyrics_search_url = re.sub('/api', '', self.lyrics_url)
    self.__custom_url: str | None = None
    pass
  def get_url(self, artist: str, title: str):
    return (self.lyrics_url + '/' + (urllib.parse.quote(artist + '/' + title)) if self.__custom_url == None else self.__custom_url).lower()
  def get(self, artist: str, title: str) -> tuple[str | None, str]:
    url = self.get_url(artist, title)
    try:
      response = requests.get(url)
      return (self.format(response.json()['lyrics']), url)
    except:
      return (None, url)
  def get_to_file(self, file: str, artist: str, title: str, custom_lyrics: str | None = None) -> tuple[str | None, str]:
    (lyrics, url) = self.get(artist, title) if custom_lyrics == None else (custom_lyrics, '')
    if lyrics != None:
      f = open(file, 'w', encoding='utf-8')
      f.write(lyrics)
      return (lyrics, url)
    return (None, url)
  def format(self, lyrics: str) -> str:
    return re.sub(r'\[.*\]\n', r'\r', re.sub(r'\n{2}', r'\r', lyrics))
  

class Genre:
  def __init__(self, page_url: str = 'https://www.last.fm/music', excluded_genres: list[str] = [], included_genres: list[str] = [], replacements: dict[str, str] = {}):
    self.page_url = page_url
    self.excluded_genres = excluded_genres
    self.included_genres = included_genres
    self.replacements = replacements
    self.__parse = True

    pass
  def isValid(self, genre: str):
    # Searches for specific string which is in 'included_genres' but not in 'excluded_genres'
    if len(self.excluded_genres) > 0 and len(self.included_genres) > 0:
      new_included = list(filter(lambda included: included not in self.excluded_genres , self.included_genres))
      for excluded in self.excluded_genres:
        if re.match(excluded, genre) != None:
          return False
      for included in new_included:
        if re.search(included, genre) != None:
          return True
      return False
    elif len(self.excluded_genres) > 0:
      for excluded in self.excluded_genres: 
        if re.search(excluded, genre) == None:
          return True
      return False
    elif len(self.included_genres) > 0:
      for included in self.included_genres:
        if re.search(included, genre) != None:
          return True
      return False
    else:
      return True
  def parse(self, value: bool):
    self.__parse = value
  def __replace_genres(self, text: str):
    newText = text
    for regex in self.replacements.keys():
      newText = re.sub(regex, self.replacements[regex], newText)
    return newText
  def get_url(self, artist: str, title: str) -> str:
    _artist = urllib.parse.quote_plus(artist) if self.__parse else re.sub('/$', '', re.sub('^/', '', artist))
    _title = urllib.parse.quote_plus(title) if self.__parse else re.sub('/$', '', re.sub('^/', '', title))
    url = (self.page_url + '/' + _artist + '/' + _title + '/+tags').lower()

    page = requests.get(url)
    if not page.ok and self.__parse == False:
      self.parse(True)
      return self.get_url(artist, title)
    return url
    
  def get(self, artist: str, title: str):
    page = requests.get(self.get_url(artist, title))
    soup = BeautifulSoup(page.content, 'html.parser')

    selection = soup.select(f'h3 a[href^="/tag"]')
    genres: list[str] = []
    for s in selection:
      genres.append(self.__replace_genres(uppercase(s.text)))
      
    filtered = set(filter(lambda genre: self.isValid(genre), genres))
    return filtered
  def get_str(self, artist: str, title: str, prefix: str | None = None, suffix: str | None = None, splitter: str = ' '):
    new_str = ''
    pre = prefix if prefix != None else ''
    suf = suffix if suffix != None else ''
    genres = self.get(artist, title)
    if len(genres) == 0:
      return '-'

    for genre in genres:
      new_str += pre + genre + suf + splitter
    return new_str