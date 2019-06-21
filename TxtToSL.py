import requests

import os

import re

from bs4 import BeautifulSoup

from yaspin import yaspin

import argparse

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # Hide pygame / moviepy startup / welcome message

from moviepy.editor import VideoFileClip, concatenate_videoclips

cache = True

version = "0.1.1"

phrases = []

class ansi:
	BLUE = '\033[94m'
	YELLOW = '\033[93m'
	GREEN = '\033[92m'
	RED = '\033[91m'

	BOLD = '\033[1m'

	END = '\033[0m'

def signorg_getpage(word):
  global cache, lang

  with yaspin(text="Getting main page for word '{}'".format(word)) as sp:
    if not os.path.isfile('cache/{}/words/{}.mp4'.format(lang.lower(), word.replace(' ', '-'))) or not cache:
      if lang == "BSL":
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
  global cache, lang

  page = signorg_getpage(word)

  if page == "cache":
    return page
  
  soup = BeautifulSoup(page, features="html.parser")
  vids = soup.find_all('source');

  for vid in vids:
    url = vid['src']

    provider = re.search("{}\/.*\/".format(lang.lower()), url).group().replace("{}/".format(lang.lower()), '').replace('/mp4/', '').replace('/', '')

    with yaspin(text="Getting video for '{}' with provider '{}'".format(word, provider)) as sp:
      r = requests.get(url)

      if r.status_code == 200:
        sp.ok(ansi.GREEN + "✓" + ansi.END)

        return r.content
      else:
        sp.fail(ansi.RED + "✗" + ansi.END)

def dgs_getpage(word):
  global cache

  with yaspin(text="Getting main page for word '{}'".format(word)) as sp:
    if not os.path.isfile('cache/dgs/words/{}.mp4'.format(word.replace(' ', '-'))) or not cache:
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
  global cache

  page = dgs_getpage(word)

  if page == "cache":
    return page
  
  entry = dgs_entrypage(page, word)

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
  global lang

  with yaspin(text="Saving video file 'cache/{}/words/{}.mp4'".format(lang.lower(), word.replace(' ', '-'))) as sp:
    if content != "cache":
      with open('cache/{}/words/{}.mp4'.format(lang.lower(), word.replace(' ', '-')), 'wb') as f:
        f.write(content)

      sp.ok(ansi.GREEN + "✓" + ansi.END)

  return True

full = None
lang = None

def getargs():
  global cache, full

  parser = argparse.ArgumentParser()

  parser.add_argument("-c", "--cache", type=int,
                      help="whether to use and save local cache", default=True)
	
  parser.add_argument("-i", "--input",
                      help="the input to translate", default=None)

  parser.add_argument("-l", "--lang",
                      help="the sign language to use", default=None, choices=["BSL", "ASL", "DGS"])

  args = parser.parse_args()
	
  cache = args.cache
  full = args.input
  lang = args.lang

def checkdir(path):
  with yaspin(text="Checking '{}' exists".format(path)) as sp:
    if not os.path.exists(path):
      sp.text = "'{}' Doesn't exist, creating".format(path)
      os.mkdir(path)
    else:
      sp.text = "'{}' Exists".format(path)

    sp.ok(ansi.GREEN + "✓" + ansi.END)

def checklang(lang):
  checkdir('cache/{}/'.format(lang))
  checkdir('cache/{}/words/'.format(lang))

def checkcache():
  checkdir('cache/') # Cache Root

  checklang('bsl') # BSL
  checklang('asl') # ASL
  checklang('dgs') # DGS

def loadphrases():
  global phrases

  if not os.path.isfile('phrases.txt'):
    with yaspin(text="Downloading 'phrases.txt'") as sp1:
      r = requests.get("https://oojmed.com/TxtToSL/phrases.txt")

      if r.status_code == 200:
        with open('phrases.txt', 'wb') as f:
          f.write(r.content)

        sp1.ok(ansi.GREEN + "✓" + ansi.END)

        return r.content
      else:
        sp1.fail(ansi.RED + "✗" + ansi.END)
  
  with yaspin(text="Loading phrases from 'phrases.txt'") as sp2:
    phrases = []

    with open('phrases.txt', 'r') as f:
      phrases = f.readlines()

    phrases = [phrase.strip() for phrase in phrases]

    sp2.ok(ansi.GREEN + "✓" + ansi.END)
  
  print()

  for phrase in phrases:
    print(phrase)

def interpret(full):
  full = full.lower() # Replacing grammar and making text low case
  full = full.replace('.', '').replace(',', '').replace('?', '')

  print(full)

  for phrase in phrases: # Phrase Recognition - Phase 1 - Finding and replacing spaces in phrases
    full = full.replace(phrase, phrase.replace(' ', '({[SPACE]})'))

  words = full.split(" ")

  print(words)

  words[:] = [word.replace('({[SPACE]})', ' ') for word in words] # Phrase Recog. - Phrase 2 - Replacing fake space with real one in phrases

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
  print("{}TxtToSL{} {}v{}{} - {}Made by{} {}Oojmed{}\n".format(ansi.YELLOW, ansi.END, ansi.RED, version, ansi.END, ansi.BLUE, ansi.END, ansi.GREEN, ansi.END))

  getargs()

  checkcache()

  print()

  loadphrases()

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

  if full == None:
    full = input("\nInput: ")

  words = interpret(full)

  for word in words:
    if lang == "BSL" or lang == "ASL":
      content = signorg_getvid(word)

      if content != "cache":
        savevid(content, word)
    elif lang == "DGS":
      content = dgs_getvid(word)

      if content != "cache":
        savevid(content, word)

    print()     

  with yaspin(text="Merging video files") as sp1: # Use pymovie to combine video files
    clips = []

    for word in words:
      clips.append(VideoFileClip("cache/{}/words/{}.mp4".format(lang.lower(), word.replace(' ', '-'))))

    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile("finished.mp4", fps=30)

    sp1.ok(ansi.GREEN + "✓" + ansi.END)

  if not cache:
    with yaspin(text="Deleting video files (because caching is disabled)") as sp2: # Use pymovie to combine video files
      for word in words:
        os.remove("cache/{}/words/{}.mp4".format(lang.lower(), word.replace(' ', '-')))

      sp2.ok(ansi.GREEN + "✓" + ansi.END)

if __name__ == "__main__":
  main()