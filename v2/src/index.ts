import { searchAction } from './search'
import terminal, { question, readline } from './utils'

init()
async function init() {
	let run = true
	do {
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
				run = false
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
		case 2:
			return null
		default:
			return options[optionId]
	}
}
