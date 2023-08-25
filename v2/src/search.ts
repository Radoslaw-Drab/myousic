import { API_BASE_URL } from './constants'
import terminal, { question } from './utils'

import { ReturnData } from './types.modal'

export async function searchAction() {
	// console.clear()
	terminal.line()
	const term = await question('Search term: ')

	const formattedTerm = encodeURI(term.replace(/ /g, '+'))
	const searchTerm = `${API_BASE_URL}/search?term=${formattedTerm}&limit=200`
	const response = await fetch(searchTerm)
	const data: ReturnData = await response.json()

	console.log(searchTerm, data)
}
