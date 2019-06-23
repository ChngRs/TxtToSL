# TxtToSL Changelog

## v0.3.0
### Interpretation
- Added autoskip, it will automatically skip words during interpretation, mostly just simple words that don't exist in sign (`is`, `the`, etc.)

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