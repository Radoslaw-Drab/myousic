const config: Config = {
	resultMaxLength: 75,
	resultInfoGap: 7,
	resultSorting: 'track',
	resultSortingOrder: 'asc'
}
export default config

interface Config {
	resultMaxLength: number | null
	resultInfoGap: number
	resultSorting: Sorting
	resultSortingOrder: SortingOrder
}
type Sorting = 'artist' | 'track' | 'album' | 'year'
type SortingOrder = 'asc' | 'desc'
