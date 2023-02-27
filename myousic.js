const { exec } = require('child_process')
const { copyrights, lineBreaker, question, errorPrompt, getCommands, readline } = require('./utils')

const BASE_URL = 'https://itunes.apple.com/search'

const KEYWORDS = ['clipboard', 'open', 'open-lyrics', 'open-image', 'url', 'download']
const KEYWORD_VALUES = [
	'search',
	'url',
	'limit',
	'sort-artist',
	'sort-track',
	'sort-album',
	'sort-year',
	'artist',
	'track',
	'album',
	'year'
]

const SETTINGS = require('./settings.json')
const ARTWORK_SIZE = SETTINGS.ARTWORK_SIZE || 1000
const DEFAULT_AUDIO_FORMAT = SETTINGS.DEFAULT_AUDIO_FORMAT || 'm4a'
const MUSIC_FOLDER = SETTINGS.MUSIC_FOLDER || '~/Music/Music/Media.localized/Automatically Add to Music.localized/'
const ARTWORK_FORMAT = SETTINGS.ARTWORK_FORMAT || 'jpg'
const WINDOW_SCALING = SETTINGS.WINDOW_SCALING || 'auto'
const DEFAULT_LIMIT = SETTINGS.DEFAULT_LIMIT || 100

const properties = getProperties()

script()

async function script() {
	console.clear()
	const clipboard = (await getCommands('pbpaste'))[0].value

	const getFromClipboard = properties.clipboard && clipboard
	const getFromSearch = properties.search?.replace(/\..*/g, '').toString()
	const getFromUrl = properties.url === true
	const url = getFromUrl ? clipboard : properties.url

	const youtubeName =
		properties.url &&
		(await getCommands(`yt-dlp -x -f ${DEFAULT_AUDIO_FORMAT} --audio-quality 0 --print "%(title)s" ${url}`))[0]?.value
			?.replace(/(\(|\[).*(\)|\])/gi, '')
			.replace(/\(*(ft|feat).*/gi, '')

	const term = youtubeName || getFromClipboard || getFromSearch || (await question('What to search: '))

	const attributes = {
		term,
		entity: 'song',
		limit: properties.limit?.replace(/\D/g) || DEFAULT_LIMIT
	}

	const formattedAttributes = Object.keys(attributes).reduce((str, attribute, i) => {
		const encodedAtt = encodeURIComponent(attributes[attribute])
		const att = `${i > 0 ? '&' : ''}${attribute}=${encodedAtt}`
		return encodedAtt ? (str += att) : str
	}, '?')

	fetch(BASE_URL + formattedAttributes)
		.then((response) => {
			if (!response.ok) {
				console.clear()
				const errorText = `ERROR\nCode: ${response.status}\nStatus: ${response.statusText}`
				lineBreaker()
				console.error(errorText)
				lineBreaker()
				return
			}
			return response.json()
		})
		.then(async (data) => {
			function sort(a, b) {
				let searchType = 'trackName'
				const sortOptions = ['asc', 'desc']
				let sort = sortOptions[0]

				let prop = ''
				function setOptions(test, type) {
					if (typeof properties[test] === 'string') {
						prop = test
						searchType = type
					}
				}
				setOptions('sortAlbum', 'collectionName')
				setOptions('sortYear', 'releaseDate')
				setOptions('sortArtist', 'artistName')
				setOptions('sortTrack', 'trackName')

				if (typeof properties[prop] === 'string') {
					sort = sortOptions.find((opt) => opt === properties[prop]) || sortOptions[0]
				}

				let sortDir = 1
				if (sort === 'desc') {
					sortDir *= -1
				}

				return a[searchType].localeCompare(b[searchType]) * sortDir
			}
			function filter(song) {
				const { track, artist, album, year } = properties
				const { trackName, artistName, collectionName, releaseDate } = song
				const sameTrack = track ? trackName.toLowerCase().includes(track.toLowerCase()) : true
				const sameArtist = artist ? artistName.toLowerCase().includes(artist.toLowerCase()) : true
				const sameAlbum = album ? collectionName.toLowerCase().includes(album.toLowerCase()) : true
				const sameYear = year ? (new Date(releaseDate).getFullYear().toString() || '').includes(year.toLowerCase()) : true
				return sameTrack && sameArtist && sameAlbum && sameYear
			}

			if (!data) return

			const results = data.results
			let songData = undefined

			let songId = 0
			if (results.length > 1) {
				const offset = 7
				let maxWidth_track = 50
				let maxWidth_artist = 25
				let maxWidth_collection = 30

				if (WINDOW_SCALING === 'auto') {
					const windowWidth = process.stdout.columns
					const availableWidth = windowWidth - 30 - offset * 3

					maxWidth_track = Math.round(availableWidth * 0.5)
					maxWidth_artist = Math.round(availableWidth * 0.25)
					maxWidth_collection = Math.round(availableWidth * 0.25)
				}

				const res = [...results].sort(sort).filter(filter)

				res.unshift({})

				const songs = res.reduce((prev, cur, id) => {
					if (id === 0) {
						return (prev +=
							''.padEnd(5) +
							limitLength('Name', maxWidth_track) +
							'| ' +
							limitLength('Artist', maxWidth_artist) +
							'| ' +
							'Year'.padEnd(5) +
							'| ' +
							limitLength('Album', maxWidth_collection) +
							'\n|  ')
					}

					const trackName = limitLength(cur.trackName, maxWidth_track)
					const artistName = limitLength(cur.artistName, maxWidth_artist)
					const collectionName = limitLength(cur.collectionName, maxWidth_collection)
					const year = (new Date(cur.releaseDate).getFullYear() || '').toString().padEnd(5)

					const song = trackName + '| ' + artistName + '| ' + year + '| ' + collectionName
					const songId = (id - 1).toString().padStart(3)
					return (prev += `${songId}: ${song}\n|  `)

					function limitLength(text, maxWidth) {
						const isLongerThanMax = text.length > maxWidth
						return text
							.padEnd(maxWidth)
							.substring(0, maxWidth)
							.padEnd(maxWidth + (isLongerThanMax ? 3 : 0), '.')
							.padEnd(maxWidth + offset)
					}
				}, '|\n|  ')

				console.clear()
				lineBreaker()
				console.log(songs)
				lineBreaker()

				songId = +(await question('|  Which song to choose (ID): '))

				lineBreaker()
			}
			songData = results[songId]

			console.clear()
			if (songData === undefined) {
				errorPrompt('Song not found')
				return
			}

			const d = getData(songData)

			lineBreaker()
			console.log(d.prompt)
			copyrights()
			lineBreaker()

			if (d.data.lyrics && (properties.open || properties.openLyrics)) exec(`open ${d.data.lyrics}`)
			if (d.data.artwork && (properties.open || properties.openImage)) exec(`open ${d.data.artwork}`)

			properties.download && url && downloadSong(url, d.data)
			readline.close()
			return
		})
	function getData(song) {
		const LYRICS_BASE_URL = 'https://www.azlyrics.com/lyrics/'
		const date = new Date(song.releaseDate)
		const artwork = song.artworkUrl100?.replace('100x100bb.jpg', `${ARTWORK_SIZE}x${ARTWORK_SIZE}bb.jpg`)
		const time = {
			minutes: Math.floor(song.trackTimeMillis / 1000 / 60)
				.toString()
				.padStart(2, '0'),
			seconds: Math.round((song.trackTimeMillis / 1000) % 60)
				.toString()
				.padStart(2, '0')
		}
		const replaceRegex = new RegExp(/\(*(ft|feat).*/, 'gi')
		const lyrics =
			LYRICS_BASE_URL +
			(
				song.artistName.replace(replaceRegex, '').replace(/\W/g, '') +
				'/' +
				song.trackName.replace(replaceRegex, '').replace(/\W/g, '') +
				'.html'
			)
				.trim()
				.toLowerCase()

		const formattedData = {
			name: song.trackName,
			artistName: song.artistName.replaceAll(' & ', ', '),
			album: song.collectionName,
			artwork,
			genre: song.primaryGenreName,
			date: date.getFullYear(),
			time: `${time.minutes}:${time.seconds}`,
			lyrics,
			track: `${song.trackNumber}/${song.trackCount}`,
			disc: `${song.discNumber}/${song.discCount}`,
			trackExplicitness: song.trackExplicitness
		}
		const formattedPrompt = Object.keys(formattedData).reduce((acc, type) => {
			return (acc += `${type}: ${formattedData[type]}\n|  `)
		}, '|\n|  ')
		return { data: formattedData, prompt: formattedPrompt }
	}
}
async function downloadSong(url, song) {
	const format = properties.format || DEFAULT_AUDIO_FORMAT

	const fileName = `${song.artistName} - ${song.name}.${format}`
	await getCommands(`yt-dlp -x -f ${format} --audio-quality 0 --add-metadata -o "${fileName}" ${url}`)

	const coverArtName = 'artwork'
	// Gets path to cover art
	const coverArtPath = `./${coverArtName}.${ARTWORK_FORMAT}`

	await getCommands(`curl --output ${coverArtPath} ${song.artwork}`)

	// Modifies metadata
	// priettier-ignore-start
	await getCommands(
		`exiftool 
    -title="${song.name}" 
    -artist="${song.artistName}" 
    -album="${song.album}" 
    -albumArtist="${song.artistName}" 
    "-coverArt<=${coverArtPath}" 
    -trackNumber="${song.track}" 
    -discNumber="${song.disc}" 
    -trackExplicitness="${song.trackExplicitness}" 
    -genre="${song.genre}" 
    -releaseDate="${song.date}" 
    -description="" 
    -longDescription="" 
    -lyrics=" " 
    "${fileName}"`
			.replaceAll(' \n', ' ')
			.replaceAll('\n', '')
	)
	// prietter-ignore-end

	// Removes cover art and moves music to Music folder
	await getCommands(
		`rm -rf ${coverArtPath}`,
		`rm -rf *_original`,
		`mv "./${fileName}" ${MUSIC_FOLDER.replace(
			/\s/g,
			// prettier-ignore
			"\\ "
		)}`
	)
	console.log('|  Download completed')
	lineBreaker()
}

function getProperties() {
	const keywords = [...KEYWORDS]
	const keywordValues = [...KEYWORD_VALUES]

	const props = {}

	keywords.forEach((keyword) => (props[formatTag(keyword)] = false))

	// Creates string out of arguments
	const args = process.argv.reduce((acc, val) => acc + ' ' + val, '')
	// Splits tags into array based on `--[tag]` and removes first one
	const allTags = args
		.trim()
		.split(/.(?=--\w*)/g)
		.slice(1)

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
