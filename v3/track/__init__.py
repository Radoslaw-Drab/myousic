from enum import Enum
from types import SimpleNamespace
from datetime import datetime
import re
import os
from pathlib import Path
import urllib.request, urllib.parse
import music_tag
from shutil import move, rmtree
from utils.colors import Color
from utils.config import Config, ReplacementProp
from track.track_data import Genre, Lyrics

cl = Color()
class Explicitness(Enum):
  notExplicit = 'notExplicit'
  explicit = 'Explicit'
class Track(dict):
  wrapperType: str = None
  kind: str
  artistId: int = None
  collectionId: int = None
  trackId: int = None
  artistName: str = None
  collectionName: str = None
  trackName: str = None
  collectionCensoredName: str = None
  trackCensoredName: str = None
  artistViewUrl: str = None
  collectionViewUrl: str = None
  trackViewUrl: str = None
  previewUrl: str = None
  artworkUrl30: str = None
  artworkUrl60: str = None
  artworkUrl100: str = None
  collectionPrice: float = None
  trackPrice: float = None
  releaseDate: str = None
  collectionExplicitness: Explicitness = None 
  trackExplicitness: Explicitness = None
  discCount: int = None
  discNumber: int = None
  trackCount: int = None
  trackNumber: int = None
  trackTimeMillis: int = None
  country: str = None
  currency: str = None
  primaryGenreName: str = None
  isStreamable: bool = None

default_track: Track = {
  'wrapperType': None,
  'kind': None,
  'artistId': None,
  'collectionId': None,
  'trackId': None,
  'artistName': None,
  'collectionName': None,
  'trackName': None,
  'collectionCensoredName': None,
  'trackCensoredName': None,
  'artistViewUrl': None,
  'collectionViewUrl': None,
  'trackViewUrl': None,
  'previewUrl': None,
  'artworkUrl30': None,
  'artworkUrl60': None,
  'artworkUrl100': None,
  'collectionPrice': None,
  'trackPrice': None,
  'releaseDate': None,
  'collectionExplicitness': None, 
  'trackExplicitness': None,
  'discCount': None,
  'discNumber': None,
  'trackCount': None,
  'trackNumber': None,
  'trackTimeMillis': None,
  'country': None,
  'currency': None,
  'primaryGenreName': None,
  'isStreamable': None,
}
class TrackExtended:
  def __init__(self, track: dict, audio_file_id: str, config: Config | None = None):
    default_track.update(**track)
    self.value: Track = SimpleNamespace(**default_track)
    self.temp_folder = config.data.temp_folder or 'tmp'
    self.output_folder = config.data.output_folder or './'
    self.default_artwork_size = max(config.data.artwork_size, 100)
    self.audio_file_id = audio_file_id
    self.config = config
    self.audio_ext = None
    self.__is_saved = False
    self.Lyrics = Lyrics()
    self.Genre = Genre(
      excluded_genres=[f'^{self.value.primaryGenreName}$', *self.config.data.excluded_genres], 
      included_genres=self.config.data.included_genres,
      replacements=self.config.data.replace_genres
    )

    self.get_dir()

  def assign_file(self, audio_ext: str):
    self.set_ext(audio_ext)
    move(self.get_file(), os.path.join(self.get_dir(), self.get_file()))
  def set_ext(self, ext: str):
    self.audio_ext = ext

  def get_dir(self, is_temporary: bool = True):
    user_regex = r'^\~\/'
    is_home = re.match(user_regex, self.output_folder) != None
    dir = Path.joinpath(Path.cwd(), self.temp_folder) if is_temporary else Path.joinpath(Path.home() if is_home else Path.cwd(), re.sub(user_regex, '', self.output_folder))
    os.makedirs(str(dir), exist_ok=True)
    return str(dir)
  def get_filename(self, is_temporary: bool = True):
    return self.audio_file_id if is_temporary else (self.value.artistName + ' - ' + self.value.trackName)
  def get_file(self, is_temporary: bool = True):
    if self.audio_ext == None:
      raise ValueError('No extension provided')
    return f'{self.get_filename(is_temporary)}.{self.audio_ext}'

  def get_child_file(self, ext: str):
    return os.path.join(self.get_dir(), f'{self.get_filename()}.{ext}')
  def get_temp_audio_path(self):
    return os.path.join(self.get_dir(True), self.get_file(True))
  def get_output_audio_path(self):
    return os.path.join(self.get_dir(False), self.get_file(False))

  def save(self):
    move(self.get_temp_audio_path(), self.get_output_audio_path())
    rmtree(self.temp_folder, ignore_errors=True)

    self.__is_saved = True


  def get_date(self):
    if self.value.releaseDate == None:
      return datetime.now()
    return datetime.strptime(self.value.releaseDate, "%Y-%m-%dT%H:%M:%SZ")
  def get_artwork_url(self, size: int = 1000):
    return re.sub('100x100', f'{max(size, 100)}x{max(size, 100)}', self.value.artworkUrl100)
  def get_lyrics_url(self):
    return self.Lyrics.get_url(self.config.modify_lyrics(ReplacementProp.ARTIST, self.value.artistName), self.config.modify_lyrics(ReplacementProp.TITLE, self.value.trackName))
  def get_artwork_ext(self):
    return re.match('\\..+$', self.value.artworkUrl100)
  def get_lyrics(self) -> tuple[str | None, str]:
    lyricsFile = self.get_child_file('txt')
    (lyrics, url) = self.Lyrics.get_to_file(lyricsFile, self.config.modify_lyrics(ReplacementProp.ARTIST, self.value.artistName), self.config.modify_lyrics(ReplacementProp.TITLE, self.value.trackName))
    return (lyrics, url)
  def check_lyrics(self):
    import requests
    return requests.get(self.get_lyrics_url()).ok
  def check_genres(self):
    import requests
    return requests.get(self.get_genres_url()).ok

  def get_genres_url(self):
    self.Genre.parse(False)
    return self.Genre.get_url(self.config.modify_genres(ReplacementProp.ARTIST, self.value.artistName), self.config.modify_genres(ReplacementProp.TITLE, self.value.trackName))
  def get_genres_str(self):
    self.Genre.parse(False)
    return self.Genre.get_str(self.config.modify_genres(ReplacementProp.ARTIST, self.value.artistName), self.config.modify_genres(ReplacementProp.TITLE, self.value.trackName), prefix='[', suffix=']')
  
  def metadata(self, get_lyrics: bool = True, get_genres: bool = True):
    if self.__is_saved:
      raise RuntimeError('Can\'t edit metadata after save')
    # Image file name
    artwork_image_filename = self.get_child_file(self.get_artwork_ext() or 'jpg')

    # Saves artwork in temp file
    with urllib.request.urlopen(self.get_artwork_url(self.default_artwork_size)) as url:
      with open(artwork_image_filename, 'wb') as f:
        f.write(url.read())
    artworkImage = open(artwork_image_filename, 'rb')

    audio = music_tag.load_file(self.get_temp_audio_path())
    audio['title'] = self.value.trackName
    audio['artist'] = self.value.artistName
    audio['composer'] = self.value.artistName
    audio['album-artist'] = self.value.artistName
    audio['album'] = self.value.collectionName
    audio['genre'] = self.value.primaryGenreName
    audio['track-number'] = self.value.trackNumber
    audio['total-tracks'] = self.value.trackCount
    audio['disc-number'] = self.value.discNumber
    audio['total-discs'] = self.value.discCount
    audio['year'] = self.get_date().year
    audio['artwork'] = artworkImage.read()

    audio.save()

    (lyrics, url) = self.get_lyrics() if get_lyrics else None
    genres = self.get_genres_str() if get_genres else None

    if genres != None:
      audio['comment'] = genres
    if lyrics != None:
      audio['lyrics'] = lyrics

    audio.save()  