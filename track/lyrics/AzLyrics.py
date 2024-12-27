import requests
import re
from bs4 import BeautifulSoup

from track.track_data import Lyrics

class AzLyrics(Lyrics):
	def __init__(self) -> None:
		super().__init__(lyrics_url='https://www.azlyrics.com/lyrics/{artist}/{title}.html')

	def get_url(self, artist: str, title: str) -> str:
		return self.lyrics_url.format(artist=re.sub(r' *', '', artist).lower(), title=re.sub(r' *', '', title).lower())

	def get(self, artist: str, title: str) -> tuple[str | None, str]:
		url = self.get_url(artist, title)

		page = requests.get(url).text
		bs = BeautifulSoup(page, 'html.parser')
		html = bs.find('div', attrs={'class': 'ringtone'})
		name = html.find_next('b').contents[0].text.strip()
		lyrics = html.find_next('div').text.strip()

		return self.format(lyrics), url