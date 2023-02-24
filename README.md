# myousic

JS script to recognise and download music you want!

- [myousic](#myousic)
- [Introduction](#introduction)
- [Instalation](#instalation)
  - [Tools](#tools)
  - [Download](#download)
- [Usage](#usage)
  - [General options](#general-options)
- [Examples](#examples)
- [Used tools](#used-tools)

# Introduction

**Hey there!**

For a long time I've been downloading music using youtube and third party software.

However I found it time consuming, even few songs took a lot of time to import to Apple Music.

<br>

That's why I've challanged myself to create a script that could automatically do it for me.

It took a few days to make using `JavaScript` and `NodeJS`, but I've managed to accomplish my task.

I've also used `yt-dlp` for downloading from YouTube link and `exiftool` for changing metadata

# Instalation

## Tools

<hr>

Tools to install:

1. [NodeJS](https://nodejs.org/en/)
2. [yt-dlp](https://github.com/yt-dlp/yt-dlp)
3. [exiftool](https://exiftool.org/) ([GitHub](https://github.com/exiftool/exiftool))

## Download

<hr>

Download code from [GitHub](https://github.com/Radoslaw-Drab/myousic) or using [git](https://git-scm.com/):`

1. Install git
2. In console (CLI) move to directory you want script to be saved to using `cd`
3. Type:

```bash
git clone https://github.com/Radoslaw-Drab/myousic
```

# Usage

```bash
node myousic.js [OPTIONS]
```

<br>

## General options

<hr>

Every option with argument has to be separated with space (quotation marks are optional, but preffered). Order does not matter.

Example:

```bash
node myousic.js --search "Linkin Park - Lost"
```

<br>

| Option          | Argument | Description                                                                                                                                    |
| --------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `--search`      | Yes      | Searches for data based on input e.g. artist name and song title                                                                               |
| `--url`         | Yes      | Searches for data based on YouTube link                                                                                                        |
| `--limit`       | Yes      | Limits search (default 100, max 200)                                                                                                           |
| `--clipboard`   | No       | Searches for data based on data inside of a clipboard                                                                                          |
| `--open`        | No       | When song is found opens artwork and lyrics inside of default browser                                                                          |
| `--open-lyrics` | No       | When song is found opens only lyrics inside of default browser                                                                                 |
| `--open-image`  | No       | When song is found opens only artwork inside of default browser                                                                                |
| `--url`         | No       | Searches for data based on YouTube link in clipboard                                                                                           |
| `--download`    | No       | Downloads music, changes metadata and moves to set folder. Works only with YouTube links, which means you have to use `--url` with this option |

# Examples

Search based on search input

```bash
node myousic.js --search "Linkin Park - Lost"
```

Search based on search input in clipboard (Data in clipboard: _Linkin Park - Lost_)

```bash
node myousic.js --clipboard
```

Search based on url

```bash
node myousic.js --url "https://youtu.be/7NK_JOkuSVY"
```

Search based on url with clipboard (Data in clipboard: _https://youtu.be/7NK_JOkuSVY_)

```bash
node myousic.js --url
```

Limits output data

```bash
node myousic.js --search "Linkin Park - Lost" --limit 20
```

Download song based on url with clipboard (Data in clipboard: _https://youtu.be/7NK_JOkuSVY_)

```bash
node myousic.js --url --download
```

Download song based on url with clipboard and opens lyrics (Data in clipboard: _https://youtu.be/7NK_JOkuSVY_)

```bash
node myousic.js --url --download --open-lyrics
```

Download song based on url with clipboard and opens lyrics and artwork (Data in clipboard: _https://youtu.be/7NK_JOkuSVY_)

```bash
node myousic.js --url --download --open
```

# Used tools

- VSCode
- [iTunes API](https://performance-partners.apple.com/search-api)
