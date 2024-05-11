import { Prefix, Suffix } from './utils'

type TrackOrCollection = 'track' | 'collection'
export type TrackOrCollectionOrArtist = TrackOrCollection | 'artist'

type Explicitness = {
	[key in Prefix<TrackOrCollection, 'Explicitness'>]: 'explicit' | 'cleaned' | 'notExplicit'
}
type CensoredName = {
	[key in Prefix<TrackOrCollection, 'CensoredName'>]: 'explicit' | 'cleaned' | 'notExplicit'
}
type ArtworkUrl = {
	[key in Suffix<'30' | '60' | '100', 'artworkUrl'>]?: string
}
type ViewUrl = {
	[key in Prefix<TrackOrCollection, 'ViewURL'>]: string
}
type Id = {
	[key in Prefix<TrackOrCollectionOrArtist, 'Id'>]: number
}
export interface Data extends Explicitness, CensoredName, ArtworkUrl, ViewUrl, Id {
	wrapperType: TrackOrCollectionOrArtist
	kind:
		| 'book'
		| 'album'
		| 'coached-audio'
		| 'feature-movie'
		| 'interactive-booklet'
		| 'music-video'
		| 'pdf-podcast'
		| 'podcast-episode'
		| 'software-package'
		| 'song'
		| 'tv-episode'
		| 'artist'
	trackName?: string
	artistName?: string
	collectionName?: string
	primaryGenreName: string
	discCount: number
	discNumber: number
	trackCount: number
	trackNumber: number
	releaseDate: string
	shortDescription?: string
	longDescription?: string
}
export interface Track extends Data {
	wrapperType: 'track'
	previewURL: string
	trackTimeMillis: number
}
export interface ApiResults {
	resultsCount: number
	results: (Track | Data)[]
}
