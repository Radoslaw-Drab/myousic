import * as fs from 'fs'
import * as crypto from 'crypto-js'
import * as path from 'path'
import * as colors from 'colors'

import { MaybePartial } from 'types/utils'

export class Config<T extends ConfigType> {
	name: string
	restartRequired: boolean
	private fileName: string
	private path: string
	private key: string | undefined
	private defaultData: MaybePartial<T>
	private extension: string = 'conf'
	constructor(fileName: string, data: MaybePartial<T>, key?: string) {
		const isProduction = process.env.NODE_ENV === 'production'
		if (!key) this.extension = 'json'
		this.name = fileName.replace(`.${this.extension}`, '')
		this.fileName = this.name + '.' + this.extension
		this.path = (isProduction ? './' : './dist/') + this.fileName
		this.key = key
		this.restartRequired = false

		if (!this.configExists()) {
			this.defaultData = data
			this.writeFile({ appName: this.name, ...data })
			this.restartRequired = false
		} else {
			this.defaultData = this.decrypt()
		}
	}
	get(): MaybePartial<T>
	get(prop: keyof T): string | null
	get(prop: (keyof T)[]): (string | null)[]
	get(prop?: (keyof T)[] | keyof T): string | null | (string | null)[] | MaybePartial<T> {
		const data = this.decrypt()
		if (prop) {
			if (Array.isArray(prop)) {
				return prop.map((p) => data[p].toString() ?? null)
			} else return data[prop]?.toString() ?? null
		} else return data
	}
	set(data: MaybePartial<T> | ((data: MaybePartial<T>) => MaybePartial<T>), restartRequired: boolean = false) {
		const currentData = this.decrypt()
		if (currentData) {
			const newData = (() => {
				switch (typeof data) {
					case 'function':
						return data(currentData)
					case 'object':
						return { ...currentData, ...data }
				}
			})()

			this.writeFile(newData, restartRequired)
		}
	}
	reset(): void {
		this.writeFile(this.defaultData)
	}
	configExists(): boolean {
		try {
			fs.readFileSync(path.resolve(this.path)).toString()
			return true
		} catch (error) {
			return false
		}
	}
	private writeFile(data: MaybePartial<T>, restartRequired: boolean = false) {
		fs.writeFile(
			path.resolve(this.path),
			this.encrypt(data),
			{
				encoding: 'utf8'
			},
			(error) => {
				if (error) console.log(colors.red.bold('Error: '), colors.red(error.message))
				if (restartRequired) this.restartRequired = true
				this.decrypt()
			}
		)
	}
	private encrypt(data: MaybePartial<T>): string {
		if (this.key) {
			return crypto.AES.encrypt(JSON.stringify(data), this.key).toString()
		} else return JSON.stringify(data)
	}
	private decrypt(): MaybePartial<T> {
		if (this.configExists()) {
			try {
				const str = fs.readFileSync(path.resolve(this.path)).toString()
				if (str) {
					if (this.key) {
						return JSON.parse(crypto.AES.decrypt(str, this.key).toString(crypto.enc.Utf8)) as T
					} else return JSON.parse(str)
				} else return {}
			} catch (error) {
				return {}
			}
		} else return this.defaultData
	}
}
type MaybeArray<T> = Array<T> | T
export type ConfigType = { [key: string]: MaybeArray<string | boolean | number> | null; appName: string }
