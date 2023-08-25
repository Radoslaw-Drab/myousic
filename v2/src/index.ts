import { searchAction } from './search'
import terminal, { question, readline } from './utils'

init()
async function init() {
	let run = true
	do {
		console.clear()
		const option = await showMenu()

		switch (option) {
			case 'search': {
				searchAction()
				break
			}
			case 'download': {
				break
			}
			case null: {
				console.clear()
				terminal.line()
				console.log('Invalid input')

				break
			}
			default: {
				run = false
				break
			}
		}
		if (run) {
			terminal.line()
			await question('Press Enter key to continue. ')
		}
	} while (run)
	readline.close()
	process.exit()
}
async function showMenu() {
	const options = ['search', 'download', 'quit']
	const optionId = await terminal.menu(options)

	switch (optionId) {
		case -1:
			return null
		case options.findIndex((option) => option === 'quit'):
			return
		default:
			return options[optionId]
	}
}
