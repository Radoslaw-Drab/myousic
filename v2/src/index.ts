import { askQuestion } from './utils'

init()
async function init() {
	const answer = await askQuestion('Test: ')
	console.log(answer)
}
function showMenu() {
	console.clear()
	console.log()
}
