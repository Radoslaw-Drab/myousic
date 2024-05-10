import { exec } from 'child_process'

export async function getCommand(command: string) {
	try {
		return await new Promise((resolve: (value: string) => void, reject) => {
			exec(command, (error, stdout) => {
				if (error) reject(error)
				return resolve(stdout.replace(/\n/g, ''))
			})
		})
	} catch (error) {
		throw new Error(error)
	}
}
export async function getCommands(...commands: string[]) {
	const promises = commands.map((command) => getCommand(command))
	const cmds = await Promise.allSettled(promises)

	type Result = {
		cmd: string
		index: number
	}
	const settled: (PromiseSettledResult<string> & Result)[] = cmds.map((value, i) => ({ ...value, cmd: commands[i], index: i }))
	return {
		settled,
		fullfilled: settled.filter((promise) => promise.status === 'fulfilled') as (Omit<PromiseFulfilledResult<string>, 'status'> &
			Result)[],
		rejected: settled.filter((promise) => promise.status === 'rejected') as (Omit<PromiseRejectedResult, 'status'> & Result)[]
	}
}
