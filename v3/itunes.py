from enum import Enum

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
  collectioName: str = None
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
