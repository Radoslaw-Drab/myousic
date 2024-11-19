# Myousic CLI

- [Myousic CLI](#myousic-cli)
  - [Overview](#overview)
  - [Features](#features)
  - [Installation](#installation)
    - [1. Installing from GitHub Releases](#1-installing-from-github-releases)
    - [2. Building from source code](#2-building-from-source-code)

## Overview

**Myousic** is a command-line interface (CLI) tool that allows you to:
1. **Download music** from YouTube using a provided YouTube link.
2. **Search for song metadata** (such as genre, artist, album, etc.) using the iTunes API.
3. **Manage the output and temporary storage** of downloaded files, including moving files to a specified folder and handling artwork.

The tool uses:
- **`yt_dlp`**: A powerful YouTube downloader and extractor.
- **`prompt_toolkit`**: For an interactive, user-friendly CLI interface.

## Features

- **Download music** directly from YouTube URLs with metadata included.
- **Search for song details** (e.g., artist, album, genre) in the iTunes database based on song metadata.
- **Flexible configuration** with options for customizing download and search behavior, genres, and more.

## Installation

You can install **Myousic** in two ways: either by downloading the latest release from GitHub or by building it from the source code.

### 1. Installing from GitHub Releases

1. Visit the [GitHub Releases page](https://github.com/RadoslawDrab/myousic/releases) for the latest version of **Myousic**.
2. Download the latest release package suitable for your operating system.


### 2. Building from source code

_Note_: You need to have Python installed on your system

1. Clone repository
```bash
git clone https://github.com/yourusername/myousic.git
cd myousic
```
2. Install dependencies
```bash
python build.py
```
Once installed, you can run the `myousic` command from the terminal:

```bash
myousic
```
It'll create `config.json` in your home directory
