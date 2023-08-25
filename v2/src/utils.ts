import { exec } from 'child_process'
import { ReadLine, createInterface } from 'readline'

export const readLine: ReadLine = createInterface({
	input: process.stdin,
	output: process.stdout
})

export async function question(question: string, expectedAnswers?: string[]): Promise<string> {
	return new Promise((resolve, reject) => {
		readLine.question(question, (answer: string) => {
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
function list(array: readonly any[], numbered?: boolean): void {
	array.forEach((item, index) => {
		const prefix: string = numbered ? `${index + 1}.` : '-'
		console.log(`${prefix} ${item}`)
	})
}
async function menu<Type extends string = string>(options: readonly Type[]): Promise<Type> {
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
			return (options[optionId - 1] || '') as Type
		} catch {
			hasError = false
		}
	} while (hasError)
	return '' as Type
}
export default {
	line,
	list,
	menu
}
