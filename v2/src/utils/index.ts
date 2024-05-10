export function loopThroughKeys<Value extends any, T extends Record<string, Value> = {}>(
	obj: T,
	callback?: (key: keyof T, value: Value, index: number) => void
) {
	return Object.keys(obj).map((key, index) => {
		callback && callback(key, obj[key], index)
		return { key, value: obj[key] }
	})
}
