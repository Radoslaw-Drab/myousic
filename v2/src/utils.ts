import { exec } from 'child_process'
import { ReadLine, createInterface } from 'readline'

export const readline: ReadLine = createInterface({
	input: process.stdin,
	output: process.stdout
})

export async function question(question: string, expectedAnswers?: string[]): Promise<string> {
	return new Promise((resolve, reject) => {
		readline.question(question, (answer: string) => {
			if (expectedAnswers && expectedAnswers.length > 0) {
				// Checks if answers is one of the expected ones
				const isCorrect = expectedAnswers.find((ans) => ans === answer) !== undefined

				if (isCorrect) resolve(answer)
				else reject()
			} else {
				resolve(answer)
			}
		})
	})
}

function line(): void {
	const windowWidth = process.stdout.columns
	console.log('-'.repeat(windowWidth || 50))
}
function list(array: string[], numbered?: boolean): void {
	array.forEach((item, index) => {
		const prefix: string = numbered ? `${index + 1}.` : '-'
		console.log(`${prefix} ${item}`)
	})
}
async function menu(options: string[]): Promise<number> {
	let hasError = false
	do {
		hasError = false
		console.clear()
		line()
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
	} while (hasError)
	return -1
}
export default {
	line,
	list,
	menu
}
