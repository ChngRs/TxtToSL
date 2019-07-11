# TxtToSL Changelog

## v0.4.0
### Documentation
- Fixed documentation in interpret()
- Linked / added demo video in README.md
- Added documentation for what we use (with links) in README.md
- Removed further documentation section in README.md
- Added a horizontal rule between sections in README.md
- Added a line break and horizontal rule between versions in CHANGELOG.md
- Updated `dgs_getvid(word)` documentation with new Signdict API stuff

### Optimization
- Moved handling no videos into `no_video(word)`
- Moved spelling out words into `spellout(word)`

### Interpretation
- Added `nl_interpret()` - It's new, experimental, very unstable, and hardly works. It uses NLTK and Natural Language Processing. It doesn't use any phrases or anything, so it fails terribly at most things, but it works very well for very simple sentances / text. This does not appear, or is referenced at all in the UI / interface. Just added for future / showcasing we tried to use NLTK?
- Added support for trying synonyms automatically if a word fails (using [Datamuse API](https://www.datamuse.com/api/))

### Fixes
- Fixed bug where phrases and autoskip won't load immediately after downloading, you would have to restart (for some reason it was returning the request content, instead of just continuing)
- Fixed bug where exception would be raised if the page could not be found / loaded for a page in BSL or ASL

### Storage
- Renamed TxtToSL/ (the data) to Data_TxtToSL/
- Also updated download link

### DGS / Signdict - Sign Gathering
- Changed to using Signdict's API, instead of a bunch of HTML parsing - Should be a lot faster
- Added `dgs_apirequest(word)` which returns the JSON of the API request (used by `dgs_getvid(word)`)
- Removed (now) old code related to the old method of gathering the video(s)

### Merging videos
- Added options when writing the finished video file which allows 4 threads (and disables audio) so it should produce the finished video file faster on better CPUs

### Interface
- Added yaspin / loader whilst creating subtitles for each clip
- Added more (ANSI) coloring
- Added command line option for automatic synonym attempting
- Print out version / start message and importing message at the start of the file, before importing anything
- Added full names for the sign languages

### Other
- Handling the content after video gathering is now done outside of the language

### Git
- Updated .gitignore to ignore the new data directory

<br>

---

## v0.3.1
### Fixes
- Fixed not creating `TxtToSL/autoskip/` directory

<br>

---

## v0.3.0
### Interpretation
- Added autoskip, it will automatically skip words during interpretation, mostly just simple words that don't exist in sign (`is`, `the`, etc.)

<br>

---

## v0.2.0
### Merging videos
- Removed Yaspin spinner from merging videos, as it clashes with moviepy's bar / loading (which looks better anyway)
- Added subtitles to resulting video / finished.mp4

### Gathering Videos - signorg (BSL + ASL)
- Made it not crash if the regex expression for getting a provider fails

### (Terminal) Interface
- Added command line / terminal option for disabling subtitles
- Made command line / terminal option for caching a bool(ean)
- Added more colour
- Added more spacing

### Interpretation
- Added support for {word} which spells out the word
- Added support for [word] which, if the word fails to be found, will automatically spell it out
- Added support for both in phrases, which performs it on the next word. Eg. My name is {}, hello []
- Replace ! with blank (removes it)

### Storage
- Only create cache language directories if selected
- Changed where things are stored
- Phrases seperate by ~~sign language~~ language

### Documentation
- Added requests requirement
- Added docstrings to functions and ANSI class

### Fixes
- Fixed crash if a space is at the end (so a word in words will be blank)