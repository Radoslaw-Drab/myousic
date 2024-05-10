import { Data } from './api'

export type Modifier = 'a' | 'artist' | 't' | 'track' | 'al' | 'album' | 'y' | 'year'
export type ModifiersObject = {
	[key in Modifier]: keyof Data
}
