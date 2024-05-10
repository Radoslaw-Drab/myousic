import * as esbuild from 'esbuild'

/** @type {esbuild.BuildOptions} */
const config = {
	entryPoints: ['src/index.ts'],
	bundle: true,
	outfile: 'dist/index.js',
	platform: 'node',
	logLevel: 'error',
	sourcemap: false,
	minify: true,
	format: 'esm'
}
await esbuild.build(config)
