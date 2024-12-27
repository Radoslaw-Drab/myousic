from track.track_data import Lyrics

class LyricsOvh(Lyrics):
	def __init__(self) -> None:
		super().__init__(lyrics_url='https://api.lyrics.ovh/v1')