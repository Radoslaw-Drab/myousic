export function loopThroughKeys<Value extends any, T extends Record<string, Value> = {}>(
	obj: T,
	callback?: (key: keyof T, value: Value, index: number) => void
) {
	return Object.keys(obj).map((key, index) => {
		callback && callback(key, obj[key], index)
		return { key, value: obj[key] }
	})
}

export function trimText(text: string, maxLength: number, minLength: number = 15) {
	const maxGreatherThanMin = maxLength > minLength
	return `${text.substring(0, maxGreatherThanMin ? maxLength - 3 : minLength)}${
		text.length >= maxLength && text.length >= minLength ? '...' : ''
	}`.padEnd(maxGreatherThanMin ? maxLength : minLength, ' ')
}