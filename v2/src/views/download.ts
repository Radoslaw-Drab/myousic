import inquirer from 'inquirer'
import cp from 'copy-paste'

import { getCommand } from 'utils/exec'
import { createTrackDataTable, createViewName, returnToMainMenuPrompt } from 'utils/prompts'
import { createObjectFromArray, mapObjectsArrayToObject, loopThroughKeys, filterObjectValues } from 'utils'

import searchView from './search'

const downloadView = (options?: { withTerm?: boolean }) =>
	new Promise<void>(async (resolve, reject) => {
		const { withTerm } = options
		createViewName('Download')

		const answer = await inquirer.prompt<{ url: string | 'clipboard' }>({
			name: 'url',
			message: 'URL',
			default: 'clipboard',
			type: 'input'
		})
		const termAnswer: { artist: string; song: string } | null = withTerm
			? await inquirer.prompt([
					{
						name: 'artist',
						message: 'Artist: ',
						type: 'input'
					},
					{
						name: 'song',
						message: 'Song: ',
						type: 'input'
					}
			  ])
			: null
		let { url } = answer
		// Checks if user wanted to get song from clipboard
		if (url === 'clipboard') {
			url = cp.paste()
		}

		if (!url.match(/https?:\/\/.*/)) {
			console.clear()
			return reject(`Invalid url: ${url}`)
		}
		// Returns url data
		const response = await getCommand(
			`yt-dlp -s --print "%(title)s;%(uploader)s;%(creator)s;%(artist)s;%(track)s;%(album)s;%(genre)s" "${url}"`
		)
		// Combines data into object
		const data = createObjectFromArray(response.split(';'), ['title', 'uploader', 'creator', 'artist', 'track', 'album', 'genre'])

		// Filters none data
		const newData = filterObjectValues(data, {
			beforeFilter: (key, value) => value !== 'NA'
		})

		let term = ''
		// Creates term
		const artist = newData.artist || newData.creator || newData.uploader
		if (newData.track || newData.artist || newData.album) {
			term = `${artist} - ${newData.track}${newData.album ? ` (${newData.album})` : ''}`
		} else if (!formatTitle(newData).includes('-')) {
			term = `${artist} - ${formatTitle(newData)}`.replace(/-(\W*|\w*)/, '- ')
			// term = `${formatTitle(newData)}`.replace(/-(\W*|\w*)/, '- ')
		} else {
			term = formatTitle(newData)
		}
		// Gets track
		try {
			const track = await searchView({ searchTerm: withTerm ? `${termAnswer.artist} - ${termAnswer.song}` : term }, downloadView)
			if (track) {
				// console.log(track)
				createTrackDataTable(track)
			}
		} catch (error) {
			console.clear()
			// console.log('>>>', error)
			return reject('There was some error: ' + error)
			// return resolve(await downloadView(true))
		}
		resolve(returnToMainMenuPrompt(downloadView))

		function formatTitle(data: typeof newData): string {
			return (
				data.title
					// .replace(new RegExp(`(?<!\\(|\\[)${artist}`), '')
					.replace(/ x /, ', ')
					.replace(/\((?=(official)|(lyrics?)|(video)).*\)/gi, '')
					.trim()
			)
		}
	})
export default downloadView
