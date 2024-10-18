import requests
import re
import urllib.parse
from bs4 import BeautifulSoup

from utils.text import uppercase

class Lyrics:
  def __init__(self, lyrics_url: str = 'https://lyrist.vercel.app/api'):
    self.lyrics_url = lyrics_url
    self.__custom_url: str | None = None
    pass
  def get_url(self, artist: str, title: str):
    return (self.lyrics_url + '/' + (urllib.parse.quote(artist + '/' + title)) if self.__custom_url == None else self.__custom_url).lower()
  def get(self, artist: str, title: str) -> str | None:
    try:
      response = requests.get(self.get_url(artist, title, self.__custom_url))
      return re.sub(r'\[.*\]\n', r'\r', re.sub(r'\n{2}', r'\r', response.json()['lyrics']))
    except:
      return None
  def get_to_file(self, file: str, artist: str, title: str):
    lyrics = self.get(artist, title)
    if lyrics != None:
      f = open(file, 'w', encoding='utf-8')
      f.write(lyrics)
      return lyrics
    return None
  

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
  def get_url(self, artist: str, title: str):
    _artist = urllib.parse.quote_plus(artist) if self.__parse else re.sub('/$', '', re.sub('^/', '', artist))
    _title = urllib.parse.quote_plus(title) if self.__parse else re.sub('/$', '', re.sub('^/', '', title))
    # return (self.page_url + '/' + urllib.parse.quote_plus(artist) + '/' + urllib.parse.quote_plus(title) + '/+tags').lower()
    # return (self.page_url + '/' + re.sub('/$', '', artist) + '/' + re.sub('/$', '', title) + '/+tags').lower()
    return (self.page_url + '/' + _artist + '/' + _title + '/+tags').lower()
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
    for genre in self.get(artist, title):
      new_str += pre + genre + suf + splitter
    return new_str