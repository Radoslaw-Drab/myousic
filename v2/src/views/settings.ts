import { createViewName, returnToMainMenuPrompt } from 'utils/prompts'

const settingsView = () =>
	new Promise<void>(async (resolve) => {
		createViewName('Settings')

		resolve(returnToMainMenuPrompt(settingsView))
	})
export default settingsView
