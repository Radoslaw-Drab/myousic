import inquirer from 'inquirer'

/** @description Shows custom name to the console */
export function createViewName(name: string) {
	console.log(`--- ${name} ---`)
}
/** @description Creates prompts which allows user to return to main menu or proceed with current view again  */
export async function returnToMainMenuPrompt<T>(currentView: (...options: any) => Promise<T>, ...options: any) {
	const { returnToMainMenu } = await inquirer.prompt<{ returnToMainMenu: boolean }>({
		name: 'returnToMainMenu',
		message: 'Return to main menu',
		type: 'confirm',
		default: true
	})
	console.clear()
	return returnToMainMenu ? null : await currentView(...options)
}
