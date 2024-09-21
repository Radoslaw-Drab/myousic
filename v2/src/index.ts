import inquirer from 'inquirer'
import pressToContinue from 'inquirer-press-to-continue'

import search from 'views/search'
import settings from 'views/settings'
import download from 'views/download'

import { Config } from 'utils/class'
import { toAbsolute } from 'utils'

import { Settings } from 'types/app'

inquirer.registerPrompt('press-to-continue', pressToContinue)

async function init() {
	const config = new Config<Settings>('settings', {
		appName: 'myousic',
		ytDlpPath: '/opt/homebrew/opt/yt-dlp/libexec/bin',
		artworkFormat: 'jpg',
		audioFormats: ['alac', 'aac', 'm4a', 'mp3'],
		artworkSize: 1000,
		saveFolder: toAbsolute('./Music'),
		includeExplicitContentByDefault: false
	})

	console.clear()
	const { menu } = await inquirer.prompt<{ menu: 'search' | 'download' | 'settings' | 'exit' }>({
		name: 'menu',
		prefix: '',
		message: '--- Myousic ---',
		type: 'list',
		choices: [
			{
				name: 'Download',
				value: 'download'
			},
			{
				name: 'Search',
				value: 'search'
			},
			{
				name: 'Settings',
				value: 'settings'
			},
			new inquirer.Separator(),
			{
				name: 'Exit',
				value: 'exit'
			}
		]
	})
	console.clear()

	try {
		switch (menu) {
			case 'search':
				await search()
				break
			case 'download':
				await download({ config })
				break
			case 'settings':
				await settings({ config })
				break
			default:
				return
		}
		await init()
	} catch (error) {
		await inquirer.prompt({
			name: 'wait',
			message: `There was an error: ${error}.\nPress any key to continue: `,
			type: 'press-to-continue',
			anyKey: true
		})
		await init()
	}
}
init()
