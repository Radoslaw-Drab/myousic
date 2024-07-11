import { ModifiersObject } from 'types/app'

export interface Config {
	baseDataUrl: string
	baseLyricsUrl: string
	searchModifiers: ModifiersObject
}
const config: Config = {
	baseDataUrl: 'https://itunes.apple.com/search',
	baseLyricsUrl: 'https://www.azlyrics.com/lyrics/',
	searchModifiers: {
		a: 'artistName',
		artist: 'artistName',
		t: 'trackName',
		track: 'trackName',
		al: 'collectionName',
		album: 'collectionName',
		y: 'releaseDate',
		year: 'releaseDate'
	}
}
export default config
