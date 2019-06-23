import requests

import os

import re

from bs4 import BeautifulSoup

from yaspin import yaspin

import argparse

import copy

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # Hide pygame / moviepy startup / welcome message

from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

cache = True
subtitles = True

version = "0.2.0"

phrases = []

class ansi:
  '''
  Contains ANSI escape characters for ANSI colour in the terminal.
  '''

  BLUE = '\033[94m'
  YELLOW = '\033[93m'
  GREEN = '\033[92m'
  RED = '\033[91m'

  BOLD = '\033[1m'

  END = '\033[0m'

def no_video_prompt(word):
  '''
  Displays prompt when there are no videos avaliable for a word.
  Depends on global variables: lang

  :param word: Word to process.
  :returns: What to return in the upper method (the method that ran it).
  '''

  global lang

  while True:
      print("{}No videos found for '{}'.{} Please choose an option:\n1) Spellout\n2) Skip\n3) Abort (Exit Program)".format(ansi.RED, word, ansi.END))
      innum = input("Number: ")

      if innum == "1":
        print("{}Spellout{}".format(ansi.BLUE, ansi.END))
        letters = list(word)

        for char in letters:
          if lang == "BSL" or lang == "ASL":
            content = signorg_getvid(char)
          elif lang == "DGS":
            content = dgs_getvid(char)

          if content != "cache":
            savevid(content, char)
        
        return letters
      elif innum == "2":
        return False
      elif innum == "3":
        exit()

def signorg_getpage(word):
  '''
  Gets page of word using signbsl.com or signasl.org (uses global variable lang to dictate which to use)
  Depends on global variables: cache, lang

  :param word: Word to get page for.
  :returns: Returns HTML content / page for that word.
  '''

  global cache, lang

  with yaspin(text="Getting main page for word '{}'".format(word)) as sp:
    if not os.path.isfile('TxtToSL/cache/{}/words/{}.mp4'.format(lang.lower(), word.replace(' ', '-'))) or not cache:
      if lang == "BSL": # Would use sign{}.com or sign{}.org but bsl is .com and asl is .org
        url = "https://signbsl.com/sign/{}".format(word.replace(' ', '-'))
      elif lang == "ASL":
        url = "https://signasl.org/sign/{}".format(word.replace(' ', '-'))
      
      r = requests.get(url)

      if r.status_code == 200:
        sp.ok(ansi.GREEN + "✓" + ansi.END)

        return r.content
      else:
        sp.fail(ansi.RED + "✗" + ansi.END)

        return False
    else:
      sp.ok(ansi.YELLOW + "✓" + ansi.END)

      return "cache"

def signorg_getvid(word):
  '''
  Gets video of word by getting the video sources on the page of a word (from signorg_getpage).
  Depends on global variables: cache, lang

  :param word: Word to get video for.
  :returns: Video content (mp4).
  '''

  global cache, lang

  replaced = word.replace('[', '').replace(']', '')
  page = signorg_getpage(replaced)

  if page == "cache":
    return page
  
  soup = BeautifulSoup(page, features="html.parser")
  vids = soup.find_all('source');

  if len(vids) == 0: # No videos / word not in dict.
    if word[0] == "[": # If surrounded by [], which makes it auto-do each letter
      if word[len(word) - 1] == "]":
        print("{}Auto spellout{}".format(ansi.BLUE, ansi.END))
        replaced = list(replaced)

        for char in replaced:
          content = signorg_getvid(char)

          if content != "cache":
            savevid(content, char)
        
        return replaced
    
    return no_video_prompt(replaced)

    
  for vid in vids:
    url = vid['src']

    provider = "unavaliable"

    try:
      provider = re.search("{}\/.*\/".format(lang.lower()), url).group().replace("{}/".format(lang.lower()), '').replace('/mp4/', '').replace('/', '')
    except:
      print("{}Unable to find provider{}".format(ansi.YELLOW, ansi.END))
    
    with yaspin(text="Getting video for '{}' with provider '{}'".format(word, provider)) as sp:
      r = requests.get(url)

      if r.status_code == 200:
        sp.ok(ansi.GREEN + "✓" + ansi.END)

        return r.content
      else:
        sp.fail(ansi.RED + "✗" + ansi.END)

def dgs_getpage(word):
  '''
  Gets page of word using signdict.org
  Depends on global variables: cache

  :param word: Word to get page for.
  :returns: Returns HTML content / page for that word.
  '''

  global cache

  with yaspin(text="Getting main page for word '{}'".format(word)) as sp:
    if not os.path.isfile('TxtToSL/cache/dgs/words/{}.mp4'.format(word.replace(' ', '-'))) or not cache:
      url = "https://signdict.org/search?q={}".format(word)
      r = requests.get(url)

      if r.status_code == 200:
        sp.ok(ansi.GREEN + "✓" + ansi.END)

        return r.content
      else:
        sp.fail(ansi.RED + "✗" + ansi.END)

        return False
    else:
      sp.ok(ansi.YELLOW + "✓" + ansi.END)

      return "cache"

def dgs_entrypage(page, word):
  '''
  Gets first entry and returns it's contents. in page (param).
  Depends on global variables: cache

  :param word: Word to get page for.
  :returns: Returns HTML content / page for the entry for the word.
  '''

  entryurl = None

  with yaspin(text="Getting entry page for word '{}'".format(word)) as sp:
    soup = BeautifulSoup(page, features="html.parser")
    links = soup.find_all('a');

    for link in links:
      url = link['href']

      if "/entry/" in url:
        sp.ok(ansi.GREEN + "✓" + ansi.END)

        entryurl = "https://signdict.org" + url

        break

    if entryurl == None:
      sp.fail(ansi.RED + "✗" + ansi.END)

      return False

  with yaspin(text="Getting content of entry page for '{}'".format(word)) as sp2:
    r = requests.get(entryurl)

    if r.status_code == 200:
      sp2.ok(ansi.GREEN + "✓" + ansi.END)

      return r.content
    else:
      sp2.fail(ansi.RED + "✗" + ansi.END)

      return False
  
def dgs_getvid(word):
  '''
  Gets video of word by getting the video sources on the page of a word (from dgs_getpage and dgs_entrypage).
  Depends on global variables: cache, lang

  :param word: Word to get video for.
  :returns: Video content (mp4).
  '''

  global cache

  replaced = word.replace('[', '').replace(']', '').replace(' ', '-')

  page = dgs_getpage(replaced)

  if page == "cache":
    return page
  
  entry = dgs_entrypage(page, replaced)

  if entry == False: # No entries, therefore no videos
    if word[0] == "[": # If surrounded by [], which makes it auto-do each letter
      if word[len(word) - 1] == "]":
        print("Auto spellout")
        replaced = list(replaced)

        for char in replaced:
          content = dgs_getvid(char)

          if content != "cache":
            savevid(content, char)
        
        return replaced
    
    return no_video_prompt(replaced)

  soup = BeautifulSoup(entry, features="html.parser")
  vids = soup.find_all('video');

  for vid in vids:
    url = vid['src']

    with yaspin(text="Getting video for '{}'".format(word)) as sp:
      r = requests.get(url)

      if r.status_code == 200:
        sp.ok(ansi.GREEN + "✓" + ansi.END)

        return r.content
      else:
        sp.fail(ansi.RED + "✗" + ansi.END)

def savevid(content, word):
  '''
  Saves video of param content.
  Depends on global variables: lang

  :param content: Video content to save.
  :param word: Word, used for file path.
  :returns: True.
  '''

  global lang

  replaced = word.replace('[', '').replace(']', '').replace(' ', '-')

  if content == None: # Unable to get / find word
    print("{}ERROR: Tried to save word '{}' but content is None. Press any key to skip word.{}".format(ansi.RED, word.replace('[', '').replace(']', ''), ansi.END))
    input()

    return False
  
  with yaspin(text="Saving video file 'TxtToSL/cache/{}/words/{}.mp4'".format(lang.lower(), replaced)) as sp:
    if content != "cache":
      with open('TxtToSL/cache/{}/words/{}.mp4'.format(lang.lower(), replaced), 'wb') as f:
        f.write(content)

      sp.ok(ansi.GREEN + "✓" + ansi.END)

  return True

full = None
lang = None

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def getargs():
  '''
  Gets command line / terminal arguments
  Depends on global variables: lang, cache

  :returns: Nothing.
  '''

  global cache, full, lang, subtitles

  parser = argparse.ArgumentParser()

  parser.add_argument("-c", "--cache", type=str2bool,
                      help="whether to use and save local cache (bool)", default=True)
	
  parser.add_argument("-i", "--input", type=str,
                      help="the input to translate (str)", default=None)

  parser.add_argument("-l", "--lang", type=str,
                      help="the sign language to use (str)", default=None, choices=["BSL", "ASL", "DGS"])

  parser.add_argument("-s", "--subtitles", type=str2bool,
                      help="whether to put subtitles in result / finished.mp4 (bool)", default=True)
  
  args = parser.parse_args()
	
  cache = args.cache
  full = args.input
  lang = args.lang
  subtitles = args.subtitles

def checkdir(path):
  '''
  Checks whether directory path (param) exists, if not, creates the directory.
  Depends on global variables: none.

  :param path: Directory / path to check / create.
  :returns: Nothing.
  '''

  with yaspin(text="Checking '{}' exists".format(path)) as sp:
    if not os.path.exists(path):
      sp.text = "'{}' Doesn't exist, creating".format(path)
      os.mkdir(path)
    else:
      sp.text = "'{}' Exists".format(path)

    sp.ok(ansi.GREEN + "✓" + ansi.END)

def checklang(lang):
  '''
  Checks whether directories for lang (param) exists, if not, creates them directory.
  Depends on global variables: none.

  :param lang: Sign language to check cache dirs for.
  :returns: Nothing.
  '''

  checkdir('TxtToSL/cache/{}/'.format(lang))
  checkdir('TxtToSL/cache/{}/words/'.format(lang))

def loadphrases(lang):
  '''
  Loads phrases of lang (param) to phrases (global)
  Depends on global variables: phrases

  :param lang: Sign language to get phrases for.
  :returns: Nothing.
  '''

  global phrases

  reallang = "english"
  if lang == "dgs":
    reallang = "german"
  
  if not os.path.isfile('TxtToSL/phrases/{}.txt'.format(reallang)):
    with yaspin(text="Downloading 'TxtToSL/phrases/{}.txt'".format(reallang)) as sp1:
      r = requests.get("https://oojmed.com/TxtToSL/phrases/{}.txt".format(reallang))

      if r.status_code == 200:
        with open('TxtToSL/phrases/{}.txt'.format(reallang), 'wb') as f:
          f.write(r.content)

        sp1.ok(ansi.GREEN + "✓" + ansi.END)

        return r.content
      else:
        sp1.fail(ansi.RED + "✗" + ansi.END)
  
  with yaspin(text="Loading phrases from 'TxtToSL/phrases/{}.txt'".format(reallang)) as sp2:
    phrases = []

    with open('TxtToSL/phrases/{}.txt'.format(reallang), 'r') as f:
      phrases = f.readlines()

    phrases = [phrase.strip() for phrase in phrases]

    sp2.ok(ansi.GREEN + "✓" + ansi.END)
  
  print()

  for phrase in phrases:
    print(phrase)

def interpret(full):
  '''
  Loads phrases of lang (param) to phrases (global)
  Depends on global variables: phrases

  :param lang: Sign language to get phrases for.
  :returns: Nothing.
  '''

  global phrases

  full = full.lower() # Replacing grammar and making text low case
  full = full.replace('.', '').replace(',', '').replace('?', '').replace('!', '')

  print(full)

  for phrase in phrases: # Phrase Recognition - Phase 1 - Finding and replacing spaces in phrasese
    replacedPhrase = phrase.replace(" {}", "").replace(" []", "")
    full = full.replace(replacedPhrase, replacedPhrase.replace(' ', '({[SPACE]})'))

  words = full.split(" ")

  words = list(filter(None, words)) # Remove empty strings

  print(words)

  words[:] = [word.replace('({[SPACE]})', ' ') for word in words] # Phrase Recog. - Phrase 2 - Replacing fake space with real one in phrases

  print(words)

  index = 0
  for word in words:
    for phrase in phrases:
      if " {}" in phrase:
        if word == phrase.replace(" {}", ""):
          print(word)
          
          try: # Try incase there is no next word
            words[index + 1] = "{" + words[index + 1] + "}"
          except:
            print("Fail")
      elif " []" in phrase:
        if word == phrase.replace(" []", ""):
          print(word)

          try: # Try incase there is no next word
            words[index + 1] = "[" + words[index + 1] + "]"
          except:
            print("Fail")
    
    index += 1

  print(words)

  final = []

  for word in words: # Seperate letters in a word if it is surrounded by {}
    if word[0] == "{":
      if word[len(word) - 1] == "}":
        word = word.replace('{', '').replace('}', '')
        final.extend(list(word))
    else:
      final.append(word)
  
  print(final)

  return final

def main():
  '''
  Main method.
  Depends on global variables: lang, full, cache, subtitles

  :returns: Nothing.
  '''

  global lang, full, cache, subtitles

  print("{}TxtToSL{} {}v{}{} - {}Made by{} {}Oojmed{}\n".format(ansi.YELLOW, ansi.END, ansi.RED, version, ansi.END, ansi.BLUE, ansi.END, ansi.GREEN, ansi.END))

  getargs()

  checkdir('TxtToSL/')
  checkdir('TxtToSL/phrases/')
  checkdir('TxtToSL/cache/')

  print()

  if lang == None:
    while True:
      print("Select Sign Language:\n1) BSL\n2) ASL\n3) DGS\n")
      innum = input("Number: ")

      if innum == "1":
        lang = "BSL"
        break
      elif innum == "2":
        lang = "ASL"
        break
      elif innum == "3":
        lang = "DGS"
        break

  print()

  checklang(lang.lower())

  print()

  loadphrases(lang.lower())

  if full == None:
    full = input("\nInput: ")

  words = interpret(full)

  print(words)

  for word in copy.deepcopy(words):
    if lang == "BSL" or lang == "ASL":
      content = signorg_getvid(word)

      if content != "cache" and content is not False and not isinstance(content, list):
        savevid(content, word)
      elif isinstance(content, list):
        index = words.index(word)

        words.remove(word)

        words[index:index] = content
      elif content is False: # Skip word
        words.remove(word)

    elif lang == "DGS":
      content = dgs_getvid(word)

      if content != "cache":
        savevid(content, word)

    print()     

  print(words)

  clips = []

  for word in words:
    replaced = word.replace('[', '').replace(']', '')

    if not os.path.isfile("TxtToSL/cache/{}/words/{}.mp4".format(lang.lower(), replaced.replace(' ', '-'))):
      continue

    originalClip = VideoFileClip("TxtToSL/cache/{}/words/{}.mp4".format(lang.lower(), replaced.replace(' ', '-')))

    if subtitles:
      txt = TextClip(replaced, font='Arial',
	      color='white',fontsize=24)

      txt_col = txt.on_color(size=(originalClip.w, txt.h + 30),
        color=(0,0,0), pos=('center' ,'center'), col_opacity=0.2)

      txt_mov = txt_col.set_pos(('center', 0.7), relative=True)

      composite = CompositeVideoClip([originalClip, txt_mov])
      composite.duration = originalClip.duration

      clips.append(composite)
    else:
      clips.append(originalClip)

  print(clips)

  final = concatenate_videoclips(clips, method="compose")
  final.write_videofile("finished.mp4", fps=30)

  if not cache:
    with yaspin(text="Deleting video files (because caching is disabled)") as sp2: # Use pymovie to combine video files
      for word in words:
        os.remove("cache/{}/words/{}.mp4".format(lang.lower(), word.replace(' ', '-')))

      sp2.ok(ansi.GREEN + "✓" + ansi.END)

if __name__ == "__main__":
  main()