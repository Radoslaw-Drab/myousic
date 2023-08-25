export interface ReturnData {
	results: number
	data: ReturnData[]
}
export interface ReturnedData {
	wrapperType: WrapperType
	explicitness: Explicitness
	kind: Kind
	trackName: string
	artistName: string
	collectionName: string
	censoredName: string
	artworkUrl60?: string
	artworkUrl100?: string
	viewURL: string
	previewURL?: string
	trackTimeMillis?: string
}

export interface ReturnTrack extends ReturnedData {
	previewURL: string
	trackTimeMillis: string
}

type WrapperType = 'track' | 'collection' | 'artist'
type Explicitness = 'explicit' | 'cleaned' | 'notExplicit'
type Media = 'music' | 'movie' | 'podcast' | 'musicVideo' | 'audiobook' | 'shortFilm' | 'tvShow' | 'software' | 'ebook' | 'all'
type Kind =
	| 'book'
	| 'album'
	| 'coached-audio'
	| 'feature-movie'
	| 'interactive-booklet'
	| 'music-video'
	| 'pdf'
	| 'podcast'
	| 'podcast-episode'
	| 'software-package'
	| 'song'
	| 'tv-episode'
	| 'artist'
