# TxtToSL Changelog

## v0.2.0
### Merging videos
- Removed Yaspin spinner from merging videos, as it clashes with moviepy's bar / loading (which looks better anyway)
- Added subtitles

### Gathering Videos - signorg (BSL + ASL)
- Made it not crash if the regex expression for getting a provider fails

### Interpretation
- Added support for {word} which spells out the word
- Added support for [word] which, if the word fails to be found, will automatically spell it out
- Added support for both in phrases, which performs it on the next word. Eg. My name is {}, hello []
- Replace ! with blank (remove it)

### Storage
- Only create cache language directories if selected
- Changed where things are stored
- Phrases seperate by sign language

### Documentation
- Added requests requirement
- Added docstrings to functions and ANSI class