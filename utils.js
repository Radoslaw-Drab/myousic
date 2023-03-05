const { exec } = require('child_process')
const readline = require('readline').createInterface({
	input: process.stdin,
	output: process.stdout
})
const SETTINGS = require('./settings.json')
const COMMANDS = require('./commands.json')
const KEYWORDS = require('./keywords.json')
const DEFAULT_AUDIO_FORMAT = SETTINGS.DEFAULT_AUDIO_FORMAT || 'm4a'
const MUSIC_FOLDER = SETTINGS.MUSIC_FOLDER || '~/Music/Music/Media.localized/Automatically Add to Music.localized/'
const ARTWORK_FORMAT = SETTINGS.ARTWORK_FORMAT || 'jpg'
const CMDS = {
	remove: getCommand('remove'),
	move: getCommand('move'),
	clipboard: getCommand('clipboard'),
	open: getCommand('open')
}

function lineBreaker(before = false, after = false) {
	if (before) console.log('\n')
	console.log('+' + '-'.repeat(process.stdout.columns - 1 || 100))
	if (after) console.log('\n')
}
function errorPrompt(text) {
	lineBreaker()
	console.log(`|\n|  ${text}\n|`)
	lineBreaker()
	readline.close()
}
function question(text) {
	return new Promise((resolve) => {
		readline.question(text, resolve)
	})
}
async function getCommands(...commands) {
	const promises = commands.map((command) => {
		return new Promise((resolve, reject) => {
			exec(command, (error, stdout) => {
				if (error) reject(error)
				return resolve(stdout.replaceAll('\n', ''))
			})
		})
	})
	const cmds = Promise.allSettled(promises)
	;(await cmds).forEach((cmd, i) => (cmd.cmd = commands[i]))
	return cmds
}

function copyrights() {
	lineBreaker()
	console.log('|  Provided by iTunes')
}
function getProperties(defaultOptions = '', schemes = []) {
	const keywords = [...KEYWORDS.BOOLEAN]
	const keywordValues = [...KEYWORDS.VALUES]

	const props = {}

	keywords.forEach((keyword) => (props[formatTag(keyword)] = false))

	// Creates string out of arguments
	let args = process.argv.reduce((acc, val) => acc + ' ' + val, '') + ' ' + defaultOptions

	// Returns all arguments found in schemes and arguments
	const argsFromSchemes = Object.keys(schemes).reduce((acc, key) => (args.includes(key) ? (acc += ' ' + schemes[key]) : acc), '')
	if (argsFromSchemes) args += argsFromSchemes

	// Splits tags into array based on `--[tag]` removes first one and returns only unique tags
	const allTags = [
		...new Set(
			args
				.trim()
				.split(/.(?=--\w*)/g)
				.slice(1)
		)
	]

	allTags
		// Filters to find tags only found in `keywords` array
		.filter((tag) => keywords.find((keyword) => '--' + keyword === tag))
		.forEach((tag) => {
			// Removes '--' string
			const formattedTag = tag.replaceAll('--', '')
			// Marks tag as `true`
			props[formatTag(formattedTag)] = true
		})
	allTags
		// Filters to find tags only found in `keywordValues` array
		.filter((tag) => keywordValues.find((keyword) => tag.includes('--' + keyword)))
		.forEach((tag) => {
			// Gets tag if it was set in `keywordValues` array
			const foundTag = keywordValues.find((keyword) => tag.includes('--' + keyword))
			// console.log(foundTag);
			// String to remove
			const toRemove = `--${foundTag} `
			// Gets value of the tag
			const value = tag.replace(toRemove, '')

			const hasValue = value !== toRemove.trim()
			if (!hasValue) return

			// Sets tag value
			props[formatTag(foundTag)] = value
		})

	return props
	function formatTag(keyword) {
		// Checks if tag includes minus. If so returns keyword
		if (!keyword.includes('-')) return keyword
		// Gets letter after '-'
		const letterToUpperCase = keyword.match(/(?<=\-)./g)
		// Replaces letter and minus with uppercase letter
		return keyword.replace(/-(?<=\-)./g, letterToUpperCase.toString().toUpperCase())
	}
}
async function downloadSong(url, song, properties) {
	// Gets file format
	const format = properties.format || DEFAULT_AUDIO_FORMAT

	// Gets whole file name
	const musicFile = `${song.artistName} - ${song.name}.${format}`

	// Gets lyrics file
	const lyricsFile = `lyrics-${song.id}.txt`

	// Shows prompt and paste lyrics data into lyrics file
	if (properties.addLyrics) {
		await question('|  Copy lyrics and press Enter. ')
		await getCommands(`${CMDS.clipboard} > ${lyricsFile}`)
	}

	// Gets path to cover art
	const coverArtFile = `./artwork-${song.id}.${ARTWORK_FORMAT}`
	// Saves artwork to new file
	await getCommands(`curl --output ${coverArtFile} ${song.artwork}`)

	console.log('|  Downloading...')
	// Downloads file in proper format and with proper file name
	await getCommands(`yt-dlp -x -f ${format} --audio-quality 0 --add-metadata -o "${musicFile}" ${url}`)

	// Modifies metadata
	// priettier-ignore-start
	await getCommands(
		`exiftool 
    -title="${song.name}" 
    -artist="${song.artistName}" 
    -album="${song.album}" 
    -albumArtist="${song.artistName}" 
    "-coverArt<=${coverArtFile}" 
    -trackNumber="${song.track}" 
    -discNumber="${song.disc}" 
    -trackExplicitness="${song.trackExplicitness}" 
    -genre="${song.genre}" 
    -releaseDate="${song.date}" 
    -description="${url}"
		-longDescription="" 
		-comment=""
		-"lyrics<=${lyricsFile}"
    "${musicFile}"`
			.replaceAll(' \n', ' ')
			.replaceAll('\n', '')
	)
	// prietter-ignore-end

	// Removes cover art, lyrics and moves music to Music folder
	await getCommands(
		`${CMDS.remove} ${coverArtFile}`,
		`${CMDS.remove} *_original`,
		`${CMDS.remove} ${lyricsFile}`,
		`${CMDS.move} "./${musicFile}" ${MUSIC_FOLDER.replace(
			/\s/g,
			// prettier-ignore
			"\\ "
		)}`
	)
	return new Promise((resolve) => resolve('Download completed'))
}
function getCommand(cmd) {
	return COMMANDS[platform()][cmd.toLowerCase()]
	function platform() {
		switch (process.platform) {
			case 'darwin':
				return 'mac'
			case 'linux':
				return 'linux'
			case 'win32':
				return 'win'
			default:
				return 'linux'
		}
	}
}

module.exports = {
	lineBreaker,
	errorPrompt,
	question,
	getCommands,
	copyrights,
	getProperties,
	downloadSong,
	CMDS,
	readline
}
