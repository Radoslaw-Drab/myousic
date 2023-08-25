import { exec } from 'child_process'
import { ReadLine, createInterface } from 'readline'

export const readline: ReadLine = createInterface({
	input: process.stdin,
	output: process.stdout
})

export async function question(question: string, expectedAnswers?: string[], allowEmpty: boolean = false): Promise<string> {
	return new Promise((resolve, reject) => {
		readline.question(question, (answer: string) => {
			if (expectedAnswers && expectedAnswers.length > 0) {
				// Checks if answers is one of the expected ones
				const isCorrect = expectedAnswers.find((ans) => ans === answer) !== undefined

				if (isCorrect || allowEmpty) resolve(answer)
				else reject()
			} else {
				resolve(answer)
			}
		})
	})
}
export function clipText(text: string, maxLength: number = 50) {
	// Adds ... at the of the text if text has characters' length greather than `maxLength`
	return `${text.substring(0, maxLength)}${'.'.repeat(Math.max(Math.min(text.length - maxLength, 3), 0))}`
}

function line(): void {
	const windowWidth = process.stdout.columns
	console.log('-'.repeat(windowWidth || 50))
}
function list(array: string[], numbered?: boolean): void {
	const maxNumberCharacterLength = (array.length + 1).toString().length

	array.forEach((item, index) => {
		const prefix: string = numbered ? `${index + 1}.`.padStart(maxNumberCharacterLength + 1, ' ') : '-'
		console.log(`${prefix} ${item}`)
	})
}
async function menu(options: string[], title?: string): Promise<number> {
	let hasError = false
	do {
		hasError = false
		line()
		if (title) {
			console.log(title)
			line()
		}
		list(options, true)
		line()
		try {
			const optionId: number = +(await question(
				`Option (1-${options.length}): `,
				options.map((_, index) => (index + 1).toString())
			))
			return optionId - 1
		} catch {
			hasError = false
		}
		console.clear()
	} while (hasError)
	return -1
}
export default {
	line,
	list,
	menu
}
