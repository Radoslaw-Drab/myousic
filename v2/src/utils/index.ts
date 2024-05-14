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

export function createObjectFromArray<Key extends string, T extends string[] = []>(array: T, keys: Key[]): Record<Key, string> {
	return array.reduce((obj, item, index) => {
		return { ...obj, [keys[index] ?? index]: item }
	}, {}) as Record<Key, string>
}

export function mapObjectsArrayToObject<T extends { key: string; value: any }>(array: T[], map?: (item: T, index: number) => T) {
	const mappedArray = array.map((item, index) => (map ? map(item, index) : item))

	return createObjectFromArray(
		mappedArray.map((item) => item.value),
		mappedArray.map((item) => item.key)
	)
}
export function filterObjectValues<Value, T extends Record<string, Value> = {}>(
	obj: T,
	options: {
		map?: (key: keyof T, value: Value, index: number) => { key: keyof T; value: Value }
		beforeFilter?: (key: keyof T, value: Value, index: number) => boolean
		afterFilter?: (key: keyof T, value: Value, index: number) => boolean
	}
) {
	return (
		loopThroughKeys<Value>(obj)
			.filter(({ key, value }, index) => (options.beforeFilter ? options.beforeFilter(key, value, index) : true))
			.map(({ key, value }, index) => options.map ? options.map(key, value, index): ({key, value}))
			.filter(({ key, value }, index) => (options.afterFilter ? options.afterFilter(key, value, index) : true))
			.reduce((obj, value) => {
				return { ...obj, [value.key]: value.value }
			}, {}) as Partial<T>
	)
}
