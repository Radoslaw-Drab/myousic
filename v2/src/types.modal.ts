export interface ReturnData {
	resultsCount: number
	results: ReturnedTrack[]
}
export interface ReturnedTrack {
	wrapperType: WrapperType
	explicitness: Explicitness
	kind: 'song'
	trackName: string
	trackCensoredName: string
	trackViewUrl: string
	artistName: string
	artistViewUrl: string
	collectionName: string
	collectionCensoredName: string
	collectionViewUrl: string
	collectionArtistName?: string
	collectionExplicitness: Explicitness
	censoredName: string
	artworkUrl60?: string
	artworkUrl100?: string
	previewUrl: string
	trackTimeMillis: string
	trackId: number
	artistId: number
	collectionId: number
	releaseDate: string
	primaryGenreName: string
	country: string
	discCount: number
	discNumber: number
	trackCount: number
	trackNumber: number
}

type WrapperType = 'track' | 'collection' | 'artist'
type Explicitness = 'explicit' | 'cleaned' | 'notExplicit'
