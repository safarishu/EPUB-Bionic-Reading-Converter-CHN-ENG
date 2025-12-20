# Bionic Reading Plugin for Calibre

**Version:** 1.0.1  
**Author:** dobrosketchkun  
**Calibre:** 5.0.0+

A Calibre plugin that converts EPUB books to Bionic Reading format for faster, more focused reading.

## What is Bionic Reading?

Bionic Reading is a reading method that highlights the beginning of each word to guide your eyes through text more efficiently. By bolding the first portion of words, your brain can complete the word recognition faster, potentially improving reading speed and focus.

**Example:**
> **Th**e **qui**ck **bro**wn **fo**x **jum**ps **ov**er **th**e **la**zy **do**g.

## Features

- **One-click conversion** — Select books and click the toolbar button
- **Non-destructive** — Original EPUB is backed up as ORIGINAL_EPUB format
- **Easy toggle** — Switch between bionic and original with menu options
- **Configurable boldness** — Adjust how much of each word gets bolded (25%-75%)
- **Batch processing** — Convert multiple books at once
- **Multi-language support** — Works with Latin, Cyrillic, Greek alphabets (English, French, German, Russian, etc.)

## Installation

### Method 1: From ZIP file

1. Build the plugin: `python build.py`
2. Open Calibre
3. Go to **Preferences → Plugins**
4. Click **"Load plugin from file"**
5. Select `BionicReading.zip`
6. When prompted, add to **main toolbar** and **context menu** for easy access
7. Restart Calibre

### Method 2: Command line

```bash
python build.py
calibre-customize -a BionicReading.zip
```

Then restart Calibre.

## Usage

### Applying Bionic Reading

1. Select one or more books in your library
2. Click the **"Bionic Reading"** button in the toolbar
   - Or right-click → **Bionic Reading → Apply Bionic Reading**
3. The plugin:
   - Backs up your original EPUB as `ORIGINAL_EPUB` format
   - Replaces the EPUB with the bionic version
4. Open the book normally — it's now in bionic format!

### Restoring Original

1. Select the book(s) you want to restore
2. Click the toolbar dropdown → **Restore Original**
   - Or right-click → **Bionic Reading → Restore Original**
3. The original EPUB is restored and the backup is removed

### How to Tell if Bionic is Applied

Look at the book's formats in the details panel (right side):
- **EPUB only** — Original, no bionic applied
- **EPUB + ORIGINAL_EPUB** — Bionic is applied (EPUB is the bionic version)

### Configuration

1. Go to **Preferences → Plugins**
2. Find "Bionic Reading" in the list
3. Click **"Customize plugin"**

Options:
- **Boldness ratio** (25%-75%): How much of each word to bold. Default is 50%.
- **Skip short words**: Skip 1-2 letter words entirely
- **Minimum word length**: Don't process words shorter than this

## Technical Details

- Processes `.xhtml`, `.html`, `.htm` files inside the EPUB
- Creates proper `<b>` XML elements (not string injection)
- Preserves all EPUB metadata, structure, and styling
- Skips `<script>`, `<style>`, `<code>`, `<pre>`, `<nav>`, `<math>`, `<svg>` elements
- Uses XML-safe processing to maintain EPUB validity
- Works with both EPUB2 and EPUB3

## Limitations

- Only works with EPUB format (not MOBI, AZW3, PDF, etc.)
- Does not work with logographic scripts (Chinese, Japanese kanji, Korean hanja)
- Some heavily styled EPUBs may have formatting conflicts with the bold tags

## Plugin Files

```
calibre_plugin/
├── __init__.py       # Plugin metadata & preferences
├── ui.py             # Toolbar button & menu actions
├── main.py           # EPUB processing & bionic conversion
├── config.py         # Settings dialog (Qt6)
├── build.py          # Build script to create ZIP
├── plugin-import-name-bionic_reading.txt
└── images/
    └── icon.png      # 24x24 toolbar icon 
```

## License

Same license as the original bionic-reading-epub-converter project.
