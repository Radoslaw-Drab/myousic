const path = require('path')

const config = {
	target: 'node',
	mode: 'development',
	module: {
		rules: [
			{
				test: /\.ts?$/,
				use: 'ts-loader',
				exclude: /node_modules/
			}
		]
	},
	entry: './src/index.ts',
	output: {
		path: path.resolve(__dirname, 'build'),
		filename: 'index.js'
	},
	resolve: {
		extensions: ['.ts']
	}
}

module.exports = config
