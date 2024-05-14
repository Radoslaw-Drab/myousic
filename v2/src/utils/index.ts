/**
 * @description Loops throughout object keys
 * @param {T} obj Custom object with string keys and custom values
 * @param {function} callback Custom callback to loop throught object keys
 * @returns {{key: string, value: any}[]} array of objects with key and value
 */
export function loopThroughKeys<Value, newValue extends Value = Value, T extends Record<string, Value> = {}>(
	obj: T,
	callback?: (key: keyof T, value: Value, index: number) => { key: string; value: newValue }
): { key: string; value: Value }[] {
	return Object.keys(obj).map((key, index) => {
		return callback ? callback(key, obj[key], index) : { key, value: obj[key] }
	})
}

/**
 *
 * @param {string} text text to be trimmed
 * @param {number} maxLength max text length
 * @param {number} minLength min text length
 * @returns {string} trimmed text
 * @example
 * maxLength = 10
 * minLength = 5
 * `Testing code` --> `Testing...`
 * `Test` --> `Test `
 *
 *
 */
export function trimText(text: string, maxLength: number, minLength: number = 15): string {
	const maxGreatherThanMin = maxLength > minLength
	return `${text.substring(0, maxGreatherThanMin ? maxLength - 3 : minLength)}${
		text.length >= maxLength && text.length >= minLength ? '...' : ''
	}`.padEnd(maxGreatherThanMin ? maxLength : minLength, ' ')
}
