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
	const options = ['search', 'download', 'quit'] as const
	type Options = (typeof options)[number]
	const option = await terminal.menu<Options>(options)

	switch (option) {
		case 'quit':
			return null
		default:
			return option
	}
}
