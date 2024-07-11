import inquirer from 'inquirer'
import color from 'colors'

import { Track } from 'types/api'
import { loopThroughKeys } from 'utils'

/** @description Shows custom name to the console */
export function createViewName(name: string) {
	console.log(`--- ${name} ---`)
}
/** @description Creates prompts which allows user to return to main menu or proceed with current view again  */
export async function returnToMainMenuPrompt<T, Options>(
	currentView: (...options: Options[]) => Promise<T>,
	defaultValue: boolean = true,
	...options: Options[]
) {
	const { returnToMainMenu } = await inquirer.prompt<{ returnToMainMenu: boolean }>({
		name: 'returnToMainMenu',
		message: 'Return to main menu',
		type: 'confirm',
		default: defaultValue
	})
	console.clear()
	return returnToMainMenu ? null : await currentView(...options)
}
type DistributeItem = {
	value: string
	percent?: number
	size?: number
	fill?: boolean
}
/**
 * @param reservedWidth Number to reduce distribution
 * @param clip String which will be show when text is too long
 * @param separator String which will separate items
 * @param endWithSeparator Boolean which determines whether to show separator at the end of the line
 * @param maxSize Max content size
 */
type DistributeContentOptions = {
	reservedWidth: number
	clip: string
	separator: string
	startWithSeparator: boolean
	endWithSeparator: boolean
	maxSize: number
	wrap: boolean
	clipLinks: boolean
}
/**
 * @param content Array of items to distribute. For more information see examples
 * @options
 * 
 * @example
 *
 * ```
 * // First value will take 40% of the size and the rest will fill so Banana and Orange will be 30% each
 * content = [
 * 	{
 * 		value: 'Apple',
 * 		percent: 0.4
 * 	},
 * 	{
 * 		value: 'Banana'
 * 	},
 * 	{
 * 		value: 'Orange'
 * 	}
 * ]
 * ```
 * @example
 *
 * ```
 * // Apple will take 40% of the size, Banana will take exactly 6 characters (cause it has 6 characters) and Orange will fill the rest
 * content = [
 * 	{
 * 		value: 'Apple',
 * 		percent: 0.4
 * 	},
 * 	{
 * 		value: 'Banana',
 * 		// Same as `percent: 0`
 * 		size: 0
 * 	},
 * 	{
 * 		value: 'Orange'
 *		fill: true
 * 	}
 * ]
 * ```
 * @example
 *
 * ```
 * // Apple will take 40% of the size, Banana will take exactly 15 characters and Orange will fill the rest
 * content = [
 * 	{
 * 		value: 'Apple',
 * 		percent: 0.4
 * 	},
 * 	{
 * 		value: 'Banana',
 * 		size: 15
 * 	},
 * 	{
 * 		value: 'Orange'
 * 	}
 * ]
 * ```
 */
export function distributeContent(content: DistributeItem[], options?: Partial<DistributeContentOptions>) {
	// Options
	const opt: DistributeContentOptions = {
		reservedWidth: 0,
		clip: '...',
		separator: ' | ',
		startWithSeparator: true,
		endWithSeparator: true,
		maxSize: 200,
		wrap: false,
		clipLinks: false,
		...options
	}
	// Content which will stay the same no matter the size
	const staticContent = content.filter((item) => (item.size === 0 || item.percent === 0) && !item.fill)
	// Static content characters length
	const staticContentLength = staticContent.reduce((len, item) => (len += item.value.length), 0)
	// Available width to distribute
	const availableWidth = Math.min(
		process.stdout.columns -
			(2 +
				opt.reservedWidth +
				// Width for separators
				(content.length - 1) * opt.separator.length +
				// Width if end separator is specified
				(opt.endWithSeparator ? opt.separator.trimEnd().length : 0) +
				(opt.startWithSeparator ? opt.separator.trimStart().length : 0) +
				staticContentLength),
		opt.maxSize
	)

	// Fixes percentages. If total percent is higher than 1 then divides every percent relatively
	const totalPercent = content.reduce((sum, item) => (sum += item.percent ? item.percent : 0), 0)
	content.forEach((item) => (item.percent ? (item.percent /= Math.max(totalPercent, 1)) : undefined))

	// Contents with percent values
	const percentContent = content.filter((item) => item.size === undefined && item.percent > 0)
	// Contents which will fill rest of the space
	const fillContent = content.filter((item) => (item.size === undefined && item.percent === undefined) || item.fill)
	// Content with predefined size
	const fixedContent = content.filter((item) => item.percent !== 0 && item.size > 0)
	// Size of content with percent values
	const percentContentSize = percentContent
		.map((item) => Math.round(availableWidth * item.percent))
		.reduce((sum, v) => (sum += v), 0)
	// Size of content with fixed values
	const fixedContentSize = fixedContent.reduce((sum, v) => (sum += v.size), 0)
	// Size of content which will be filled
	const fillContentSize = Math.round((availableWidth - percentContentSize - fixedContentSize) / fillContent.length)

	return content.reduce((str, item, index, array) => {
		switch (checkItemType(item)) {
			case 'static':
				return (str += addStartSeparator() + item.value + addSeparator())
			case 'fill':
				return (str += addStartSeparator() + substring(fillContentSize) + addSeparator())
			case 'percent': {
				const size = Math.round(availableWidth * item.percent)
				return (str += addStartSeparator() + substring(size) + addSeparator())
			}
			case 'size': {
				return (str += addStartSeparator() + substring(item.size, true) + addSeparator())
			}
		}
		function addStartSeparator() {
			if (index === 0 && opt.startWithSeparator) return opt.separator.trimStart()
			else return ''
		}
		// Adds separator and determines whether to add separator at the end
		function addSeparator() {
			if (index < array.length - 1) return opt.separator
			else if (index === array.length - 1 && opt.endWithSeparator) return opt.separator.trimEnd()
		}
		// Creates substring of the value
		function substring(size: number, isFixed: boolean = false) {
			// if (!opt.wrap) {
			const value = item.value.substring(0, size).padEnd(size, ' ')
			// Returns fixed value
			if (value.length === size && isFixed) return value
			// Appends `clip` value at the end of the string if it's larger than size
			if (opt.wrap && item.value.length >= size) {
				if (!opt.clipLinks && item.value.match(/https?:\/\/.*/)) return item.value

				return value + '\n' + item.value.substring(size)
			}
			return value.replace(new RegExp(`\\S{${opt.clip.length}}$`), opt.clip)
			// } else return item.value
		}
	}, '')
	// Returns item type
	function checkItemType(item: DistributeItem): 'static' | 'fill' | 'percent' | 'size' {
		if (item.percent === 0 || item.size === 0) return 'static'
		else if (item.size > 0) return 'size'
		else if (item.percent > 0) return 'percent'
		else return 'fill'
	}
}

/**
 * @param contrastedRows Whether to show every second row with different color
 */
interface TableOptions extends DistributeContentOptions {
	contrastedRows: boolean
	headerColor?: color.Color
}
export function createTable(columns: DistributeItem[], values: (string[] | null)[], options?: Partial<TableOptions>) {
	const opt: TableOptions = {
		clip: '...',
		startWithSeparator: true,
		endWithSeparator: true,
		maxSize: 200,
		reservedWidth: 0,
		separator: ' | ',
		wrap: false,
		clipLinks: false,
		contrastedRows: true,
		...options
	}
	const consoleWidth = process.stdout.columns
	const tableWidth =
		Math.max(Math.min(consoleWidth, opt.maxSize), 10) +
		(opt.startWithSeparator ? opt.separator.trimStart().length : 0) +
		(opt.endWithSeparator ? opt.separator.trimEnd().length : 0) +
		(columns.length - 1) * opt.separator.length

	const horizontalLine = '-'.repeat(tableWidth)

	const headerContent = distributeContent(columns, opt)
	const heading = opt.headerColor ? opt.headerColor(headerContent) : headerContent

	const fullHeading = `${horizontalLine}\n${heading}\n${horizontalLine}\n`
	let horizontalLinesOffset = 0
	const str =
		fullHeading +
		values.reduce((str, row, index) => {
			const isHorizontalLine = row === null
			const clr = opt.contrastedRows ? ((index + horizontalLinesOffset) % 2 === 0 ? color.gray : color.white) : null
			// if (row === null) horizontalLinesOffset++
			const content = !isHorizontalLine
				? distributeContent(
						row.map((col, index) => ({ ...columns[index], value: col })),
						opt
				  )
				: horizontalLine
			return (str += (clr && !isHorizontalLine ? clr(content) : content) + '\n')
		}, '') +
		horizontalLine
	return str
}
export function createTrackDataTable(track: Track) {
	const timeSeconds = Math.floor(track.trackTimeMillis / 1000)
	const time: string =
		Math.floor(timeSeconds / 60)
			.toString()
			.padStart(2, '0') +
		':' +
		(timeSeconds - Math.floor(timeSeconds / 60) * 60).toString().padStart(2, '0')
	const table = createTable(
		[{ value: 'Names' }, { value: 'Values', percent: 0.8 }],
		[
			['Artist', track.artistName],
			['Track', track.trackName],
			['Album', track.collectionName],
			null,
			['Year', new Date(track.releaseDate).getFullYear().toString()],
			['Time', time],
			['Explicitness', track.trackExplicitness],
			null,
			['Disc number', track.discNumber?.toString() ?? '1'],
			['Disc count', track.discCount?.toString() ?? '1'],
			['Track number', track.trackNumber?.toString() ?? '1'],
			['Track count', track.trackCount?.toString() ?? '1'],
			null,
			['Artwork URL', track.artworkUrl100.replace(/100x100/g, '1000x1000')]
		],
		{
			wrap: true
			// maxSize: 130
		}
	)
	console.log(table)
}