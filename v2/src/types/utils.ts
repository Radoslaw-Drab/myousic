export type Prefix<P extends string, C extends string> = `${P}${C}`
export type Suffix<S extends string, C extends string> = `${C}${S}`
export type MaybePartial<T> = T | Partial<T>