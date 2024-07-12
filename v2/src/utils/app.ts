import constants from 'const'

import { Track } from 'types/api'

export function getLyrics(track: Track) {
	const url = constants.baseLyricsUrl + track.artistName.toLowerCase() + '/' + track.trackName.toLowerCase() + '.html'
	return url
}
