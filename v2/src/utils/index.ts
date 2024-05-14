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
 * @param {number} currentMaxLength current max text length. E.g. With ['test', 'world'] value should be 5
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
export function trimText(text: string, currentMaxLength: number, maxLength: number, minLength: number = 15): string {
	return `${text.substring(0, currentMaxLength > maxLength ? maxLength : currentMaxLength)}`.padEnd(
		currentMaxLength ? maxLength : minLength,
		' '
	)
}
export function trim(text: string, maxLength: number): string {
	const substring = text.substring(0, maxLength)
	return `${substring.padEnd(maxLength, ' ')}`
}
