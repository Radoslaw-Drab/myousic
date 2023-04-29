const { exec } = require('child_process')
const {
	copyrights,
	lineBreaker,
	question,
	errorPrompt,
	getCommands,
	readline,
	getProperties,
	downloadSong,
	CMDS
} = require('./utils')

const BASE_URL = 'https://itunes.apple.com/search'

const SETTINGS = require('./settings.json')
const ARTWORK_SIZE = SETTINGS.ARTWORK_SIZE || 1000
const WINDOW_SCALING = SETTINGS.WINDOW_SCALING || 'auto'
const DEFAULT_LIMIT = SETTINGS.DEFAULT_LIMIT || 100
const DEFAULT_OPTIONS = SETTINGS.DEFAULT_OPTIONS
const SCHEMES = SETTINGS.SCHEMES
const EXAMPLE_DATA = {
	artistName: 'notFound',
	trackName: 'notFound',
	collectionName: 'notFound',
	trackTimeMillis: 100000,
	trackNumber: 1,
	trackCount: 1,
	discNumber: 1,
	discCount: 1,
	releaseDate: new Date().toISOString(),
	primaryGenreName: 'notFound',
	trackExplicitness: 'notFound'
}

const properties = getProperties(DEFAULT_OPTIONS, SCHEMES)

let songNotFound = false
script()

async function script() {
	console.clear()
	// Gets data from the clipboard
	const clipboard = (await getCommands(`${CMDS.clipboard}`))[0].value

	// Gets data from the clipboard if `clipboard` property is set
	const getFromClipboard = properties.clipboard && clipboard
	// Gets data from `search` property
	const getFromSearch = properties.search
	// Boolean which determines if url was set
	const getFromUrl = properties.url === true
	// Gets URL based on `url` property. Gets value from clipboard if `url` does not contain any url afterwards
	const url = getFromUrl ? clipboard : properties.url
	// Gets type from `track`, `artist`, `album` or `year` attribute
	const getFromTypes = properties.track || properties.artist || properties.album || properties.year

	// Returns song name based on YouTube title
	const songName =
		properties.url &&
		(await getCommands(`yt-dlp --print "%(title)s" ${url}`))[0]?.value
			// Replaces anything that is contained inside of [] or ()
			?.replace(/\(.*\)|\[.*\]/gi, '')
			// Replaces any ' x ' to ', '
			.replace(/ x /gi, ', ')

	lineBreaker()
	// Gets term to search based on hierarchy: question after rerunned script > url > clipboard > search > types > no properties
	const term = songNotFound
		? await question('|  Song not found. New search: ')
		: '' || songName || getFromClipboard || getFromSearch || getFromTypes || (await question('|  What to search: '))

	const attributes = {
		term,
		entity: 'song',
		// Allows to change limit
		limit: properties.limit?.replace(/\D/g) || DEFAULT_LIMIT
	}

	// Variable with every attiribute inside of `attributes` object formatted to math proper URI
	const formattedAttributes = Object.keys(attributes).reduce((str, attribute, i) => {
		// Gets encodedURI with current attribute
		const encodedAtt = encodeURIComponent(attributes[attribute])
		// Determines whether to add `&` and adds attribute to URI
		const att = `${i > 0 ? '&' : ''}${attribute}=${encodedAtt}`
		// Adds `att` to string only if `encodedAtt` is set
		return encodedAtt ? (str += att) : str
	}, '?')

	console.clear()
	// Fetches properly formatted URL
	fetch(BASE_URL + formattedAttributes)
		.then((response) => {
			// Checks whether script failed to get response. If so prints error to the console and returns
			if (!response.ok) {
				console.clear()
				const errorText = `ERROR\nCode: ${response.status}\nStatus: ${response.statusText}`
				errorPrompt(errorText)
				return
			}
			return response.json()
		})
		.then(async (data) => {
			function sort(a, b) {
				// Default searching from data received from iTunes
				let searchType = 'trackName'
				// All sort options
				const sortOptions = ['asc', 'desc']
				// Sets default sort option
				let sort = sortOptions[0]
				let prop = ''

				// Tests if property is a string and sets `prop` to proper property and `searchType` to type
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

				// Checks if property exists
				if (typeof properties[prop] === 'string') {
					// Sets sorting option if found or set's default option
					sort = sortOptions.find((opt) => opt === properties[prop]) || sortOptions[0]
				}

				let sortDir = 1
				// If sorting is set to `desc` then order will reverse
				if (sort === 'desc') {
					sortDir *= -1
				}

				// Compares strings
				return a[searchType].localeCompare(b[searchType]) * sortDir
			}
			function filter(song) {
				const { track, artist, album, year } = properties
				const { trackName, artistName, collectionName, releaseDate } = song

				// Checks whether `trackName` includes anything from `track` property
				const sameTrack = track ? trackName.toLowerCase().includes(track.toLowerCase()) : true
				// Checks whether `artistName` includes anything from `artist` property
				const sameArtist = artist ? artistName.toLowerCase().includes(artist.toLowerCase()) : true
				// Checks whether `collectionName` includes anything from `album` property
				const sameAlbum = album ? collectionName.toLowerCase().includes(album.toLowerCase()) : true
				// Checks whether `releaseDate` includes anything from `year` property
				const sameYear = year ? (new Date(releaseDate).getFullYear().toString() || '').includes(year.toLowerCase()) : true
				// Returns true only if every property is truthy
				return sameTrack && sameArtist && sameAlbum && sameYear
			}

			// Returns if no data has been received
			if (!data) return

			// Gets results
			const { results } = data
			let songData = undefined

			let songId = 0

			// Gets sorted and filtered results
			const res = [...results].sort(sort).filter(filter)

			// If results contain array with more than one elements then formats proper display
			if (res.length > 1 && !properties.downloadOnly) {
				// Offset between last element and new column
				const offset = 7
				// Max number of width for track
				let maxWidth_track = 50
				// Max number of width for artist
				let maxWidth_artist = 25
				// Max number of width for album
				let maxWidth_collection = 30

				if (WINDOW_SCALING === 'auto') {
					const windowWidth = process.stdout.columns
					const availableWidth = windowWidth - 30 - offset * 3

					maxWidth_track = Math.round(availableWidth * 0.5)
					maxWidth_artist = Math.round(availableWidth * 0.25)
					maxWidth_collection = Math.round(availableWidth * 0.25)
				}

				// Adds new result for naming
				res.unshift({})

				const songs = res.reduce((prev, cur, id) => {
					// Returns properly formatted columns naming
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

					// Gets track name  with limited length to `maxWidth_track`
					const trackName = limitLength(cur.trackName, maxWidth_track)
					// Gets artist with limited length to `maxWidth_artist`
					const artistName = limitLength(cur.artistName, maxWidth_artist)
					// Gets album name with limited length to `maxWidth_collection`
					const collectionName = limitLength(cur.collectionName, maxWidth_collection)
					// Gets year value
					const year = (new Date(cur.releaseDate).getFullYear() || '').toString().padEnd(5)

					// Properly formatted string
					const song = trackName + '| ' + artistName + '| ' + year + '| ' + collectionName
					// Properly formatted id
					const songId = (id - 1).toString().padStart(3)
					// Returns new string
					return (prev += `${songId}: ${song}\n|  `)

					function limitLength(text, maxWidth) {
						// Checks whether text length is longer than `maxWidth`
						const isLongerThanMax = text.length > maxWidth
						// Adds '...' if `isLongerThanMax` is true
						return text
							.padEnd(maxWidth)
							.substring(0, maxWidth)
							.padEnd(maxWidth + (isLongerThanMax ? 3 : 0), '.')
							.padEnd(maxWidth + offset)
					}
				}, '|\n|  ')

				// Shows all songs
				console.clear()
				lineBreaker()
				console.log(songs)
				lineBreaker()

				res.shift()

				// Gets song id based on user input
				songId = +(await question('|  Which song to choose (ID): ')) || 0

				lineBreaker()
			}
			console.clear()

			// Gets song data
			songData = res[songId]

			// Checks if song has been found. If not reruns script
			if (songData === undefined) {
				songNotFound = true
				script()
				return
			}

			// Sets default data if `downloadOnly` property is set
			if (properties.downloadOnly) {
				const EXAMPLE = { ...EXAMPLE_DATA }
				EXAMPLE.trackName = songName
				songData = EXAMPLE
			}

			// Returns object containing all data
			const d = getData(songData)

			// Downloads file only
			if (properties.downloadOnly) {
				lineBreaker()
				await download(d.data)
				readline.close()
				return
			}

			// Shows proper data prompt
			lineBreaker()
			console.log(d.prompt)
			copyrights()
			lineBreaker()

			// Opens lyrics and/or images if `open`, `openLyrics` or `openImage` property is set
			if (d.data.lyrics && (properties.open || properties.openLyrics)) exec(`${CMDS.open} ${d.data.lyrics}`)
			if (d.data.artwork && (properties.open || properties.openImage)) exec(`${CMDS.open} ${d.data.artwork}`)

			await download(d.data, songData.trackId)
			// Closes readline
			readline.close()
			return
		})
	function getData(song) {
		const LYRICS_BASE_URL = 'https://www.azlyrics.com/lyrics/'
		const GENRES_BASE_URL = 'https://genius.com/'

		const date = new Date(song.releaseDate)
		// Replaces 100x100 artwork format to desired resolution
		const artwork = song.artworkUrl100?.replace('100x100bb.jpg', `${ARTWORK_SIZE}x${ARTWORK_SIZE}bb.jpg`)
		// Returns properly formatted time of song
		const time = {
			minutes: Math.floor(song.trackTimeMillis / 1000 / 60)
				.toString()
				.padStart(2, '0'),
			seconds: Math.round((song.trackTimeMillis / 1000) % 60)
				.toString()
				.padStart(2, '0')
		}
		const genresTrackName = song.trackName
			.replace(/[^a-zA-Z0-9 ]+/gm, '')
			.replace(/\s/gm, '-')
			.toLowerCase()
		const genresArtistName = song.artistName
			.replace(/[^a-zA-Z0-9 ]+/gm, '')
			.replace(/\s/gm, '-')
			.toLowerCase()

		const otherGenres = `${GENRES_BASE_URL}${genresArtistName}-${genresTrackName}-lyrics#song-info`

		// Replaces everything inside of () with 'feat' or 'ft' inside
		const replaceRegex = new RegExp(/\(*(ft|feat).*/, 'gi')

		const artistName = song.artistName.replace(replaceRegex, '').replace(/\W/g, '')
		const trackName = song.trackName.replace(replaceRegex, '').replace(/\W/g, '')

		// Properly formats lyrics URL
		const lyrics = `${LYRICS_BASE_URL}${artistName}/${trackName}.html`.trim().toLowerCase()

		// Creates object with formatted data
		const formattedData = {
			name: song.trackName,
			artistName: song.artistName.replaceAll(' & ', ', '),
			album: song.collectionName,
			artwork,
			genre: song.primaryGenreName,
			date: date?.getFullYear(),
			time: `${time.minutes}:${time.seconds}`,
			lyrics,
			track: `${song.trackNumber}/${song.trackCount}`,
			disc: `${song.discNumber}/${song.discCount}`,
			trackExplicitness: song.trackExplicitness
		}
		if (properties.otherGenres || properties.addGenres) formattedData.otherGenres = otherGenres

		// Creates properly formatted prompt
		const formattedPrompt = Object.keys(formattedData).reduce((acc, type) => {
			return (acc += `${type}: ${formattedData[type]}\n|  `)
		}, '|\n|  ')
		return { data: formattedData, prompt: formattedPrompt }
	}
	async function download(data, id = -1) {
		let message = ''
		// Downloads file if URL is provided and `download` property is set
		if (properties.download && url) {
			const song = { ...data }
			song.id = id === -1 ? Math.round(Math.random() * 100000) : Math.round(id)

			message = await downloadSong(url, song, properties)
		}
		if (message) {
			console.log('|  ' + message)
			lineBreaker()
		}
	}
}
