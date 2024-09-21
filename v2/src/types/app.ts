import { Config } from 'utils/class'

import { Data } from './api'

export type Modifier = 'a' | 'artist' | 't' | 'track' | 'al' | 'album' | 'y' | 'year'
export type ModifiersObject = {
	[key in Modifier]: keyof Data
}

export const settings: (keyof Settings)[] = [
	'appName',
	'saveFolder',
	'artworkSize',
	'artworkFormat',
	'audioFormats',
	'ytDlpPath',
	'includeExplicitContentByDefault'
] as const
export type SettingsKey = (typeof settings)[number]

export type Settings = {
	appName: string
	saveFolder?: string
	artworkSize?: number
	artworkFormat?: 'jpg' | 'png'
	ytDlpPath: string
	audioFormats?: ('alac' | 'mp3' | 'm4a' | 'aac' | 'flac')[]
	includeExplicitContentByDefault?: boolean
}

export type AppConfig = Config<Settings>
