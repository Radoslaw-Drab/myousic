import * as esbuild from 'esbuild'

/** @type {esbuild.BuildOptions} */
const config = {
	entryPoints: ['src/index.ts'],
	bundle: true,
	outfile: 'dist/index.js',
	platform: 'node',
	logLevel: 'debug',
	sourcemap: 'inline',
	format: 'esm'
}

const context = await esbuild.context(config)
await context.watch()
