import { ReadLine, createInterface } from 'readline'

const readLine: ReadLine = createInterface({
	input: process.stdin,
	output: process.stdout
})

export async function askQuestion(question: string, expectedAnswers?: string[]): Promise<string> {
	return new Promise((resolve, reject) => {
		readLine.question(question, (answer: string) => {
			if (expectedAnswers && expectedAnswers.length > 0) {
				// Checks if answers is one of the expected ones
				const isCorrect = expectedAnswers.find((ans) => ans === answer) !== undefined

				readLine.close()
				if (isCorrect) resolve(answer)
				else reject()
			} else if (answer) {
				readLine.close()
				resolve(answer)
			} else {
				reject()
			}
		})
	})
}
