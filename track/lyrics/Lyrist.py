from track.track_data import Lyrics

class Lyrist(Lyrics):
	def __init__(self) -> None:
		super().__init__(lyrics_url='https://lyrist.vercel.app/api')