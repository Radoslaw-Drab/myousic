import { createViewName, returnToMainMenuPrompt } from 'utils/prompts'

import { AppConfig } from 'types/app'

const settingsView = (options?: { config: AppConfig }) =>
	new Promise<void>(async (resolve) => {
		const config = options?.config

		createViewName('Settings')
		console.log(config.get())

		resolve(returnToMainMenuPrompt(settingsView))
	})
export default settingsView
