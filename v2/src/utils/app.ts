import constants from 'const'

import { Track } from 'types/api'

export function getLyrics(track: Track) {
	const artist = track.artistName.toLowerCase().replace(/ /g, '')
	const name = track.trackName.toLowerCase().replace(/ /g, '')
	return constants.baseLyricsUrl + artist + '/' + name + '.html'
}
