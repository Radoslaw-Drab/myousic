import inquirer from 'inquirer'
import autocomplete from 'inquirer-autocomplete-standalone'
import color from 'colors'
import cp from 'copy-paste'

import { loopThroughKeys, loading } from 'utils'
import { createTrackDataTable, createViewName, distributeContent, returnToMainMenuPrompt } from 'utils/prompts'
import constants from 'const'

import { ApiResults, Data, Track } from 'types/api'
import { AppConfig, Modifier } from 'types/app'

const searchView = (options?: { searchTerm?: string; config: AppConfig }, originalView?: () => Promise<void>) =>
	new Promise<Track | void>(async (resolve, reject: ({ error: string, customError: boolean }) => void) => {
		const searchTerm = options?.searchTerm

		createViewName('Search')

		let search = searchTerm,
			searchType = ['artistTerm', 'songTerm'],
			explicitness = !!options?.config.get('includeExplicitContentByDefault')

		if (!searchTerm) {
			const answers = await inquirer.prompt<{
				search: string
				searchType: string[]
				explicitness: boolean
			}>([
				{
					type: 'input',
					name: 'search',
					message: 'Search term:',
					default: searchTerm ?? 'clipboard'
				},
				{
					type: 'checkbox',
					name: 'searchType',
					message: 'Search types:',
					choices: [
						{
							checked: true,
							value: 'songTerm',
							name: 'Track'
						},
						{
							checked: true,
							value: 'artistTerm',
							name: 'Artist'
						},
						{
							checked: false,
							value: 'albumTerm',
							name: 'Album'
						}
					]
				},
				{
					name: 'explicitness',
					message: 'Include explicit content',
					default: explicitness,
					type: 'confirm'
				}
			])
			if (answers.search === 'clipboard') {
				search = cp.paste()
			} else search = answers.search
			searchType = answers.searchType
			explicitness = answers.explicitness
		}

		const term = search
			.replace(/\s/g, '+')
			.replace(/(?!\+)\W/g, '')
			.replace(/\+{2,}/, '+')
			.toLowerCase()
		// const searchTypeString = '&attribute=[' + searchType.reduce((str, v, i) => (str += (i > 0 ? ',' : '') + v), '') + ']'
		// const searchTypeString = `&attribute=${searchType.reduce(
		// 	(str, v, i, arr) => (str += v + (i < arr.length - 1 ? ',' : ']')),
		// 	'['
		// )}`

		const stop = loading()

		try {
			const response = await fetch(
				`${constants.baseDataUrl}?term=${term}&media=music&explicit=${explicitness ? 'yes' : 'no'}&limit=200`
			)
			const data: ApiResults = await response.json()

			stop()

			if (!data || data.resultsCount === 0 || data.results.length === 0) {
				reject({
					error:
						`No search result for: ${color.green(search)}!` +
						` ${searchType} ` +
						` ${constants.baseDataUrl}?term=${term}&media=music&explicit=${explicitness ? 'yes' : 'no'}&limit=200`,
					customError: true
				})
				return
			}
			console.clear()
			console.log(`Search result for: ${color.green(search)}`)

			const answer = await autocomplete({
				message: 'Select:',
				pageSize: Math.min(Math.max(process.stdout.rows - 3, 5), 40),
				// @ts-expect-error unknown type error
				source: async (input: string) => {
					const resultsFiltered = data.results.filter((data) => {
						if (input) {
							return input.split(';').reduce((output, inp) => output && getFilterValue(inp), true)
						} else return true
						function getFilterValue(input: string) {
							const modifiers = loopThroughKeys<keyof Data>(constants.searchModifiers)

							for (let modifier of modifiers) {
								const key = modifier.key as Modifier
								if (input.includes(`${key}=`)) {
									switch (key) {
										case 'year':
										case 'y':
											return new Date(data[modifier.value])
												.getFullYear()
												.toString()
												.includes(input.toLowerCase().replace(`${key}=`, ''))
										default:
											return data[modifier.value]
												.toString()
												.toLowerCase()
												.includes(input.toLowerCase().replace(`${key}=`, ''))
									}
								}
							}
							return (
								data.trackName.toLowerCase().includes(input.toLowerCase()) ||
								data.artistName.toLowerCase().includes(input.toLowerCase())
							)
						}
					})
					const longestTrackName = Math.max(...resultsFiltered.map((value) => value.trackName?.length ?? 0))
					const longestArtistName = Math.max(...resultsFiltered.map((value) => value.artistName.length ?? 0))
					const longestCollectionName = Math.max(...resultsFiltered.map((value) => value.collectionName?.length ?? 0))

					const tableWidth = process.stdout.columns
					const line = ' ' + '-'.repeat(tableWidth - 2)

					return [
						{ type: 'separator', separator: line },
						...resultsFiltered.map((t, i) => {
							const name = distributeContent(
								[
									{ value: (i + 1 + '.').padEnd(4, ' '), percent: 0 },
									{
										value: t.trackName ?? '',
										percent: 0.4
									},
									// { value: t.trackName, size: longestTrackName },
									{ value: t.artistName ?? '', percent: 0.32 },
									{ value: t.collectionName ?? '' },
									{ value: new Date(t.releaseDate).getFullYear().toString(), percent: 0 }
								],
								{ reservedWidth: process.stdout.columns > 140 ? 1 : 0 }
							)
							return {
								name,
								value: t
							}
						}),
						{ type: 'separator', separator: line },
						{ name: '| Exit', value: 'exit' },
						{ type: 'separator', separator: line }
					]
				}
			})
			if (!originalView) {
				console.clear()
				createTrackDataTable(answer)
				resolve(returnToMainMenuPrompt(searchView))
			} else {
				console.clear()
				resolve(answer)
			}
		} catch (error) {
			reject({ error: color.bgRed.white('There was some error: ') + error, customError: false })
		}
	})
export default searchView
