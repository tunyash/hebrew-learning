from difflib import SequenceMatcher
import gtts
from playsound import playsound
import json
import random
import sys

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def play_hebrew_word(word):
  tts = gtts.gTTS(word, lang="iw")
  tts.save("sound.mp3")
  playsound("sound.mp3")
  
def play_to_english_round(word_desc):
  if 'to_english_score' not in word_desc or 'to_english_attempts' not in word_desc:
      word_desc['to_english_score'] = 0
      word_desc['to_english_attempts'] = 0
  print('Translate ', word_desc['hebrew'], '(' + word_desc['translit'] + ')')
  play_hebrew_word(word_desc['hebrew'])
  answer = input()
  if answer == 'STOP_GAME':
    return None
  if any(similarity(answer, word) > 0.8 for word in word_desc['english'].split()):
    print('Success: ', word_desc['english'])
    word_desc['to_english_score'] += 1
  else:
    print('Fail, correct words: ', word_desc['english'])
  word_desc['to_english_attempts'] += 1
  print('Success rate for ', word_desc['hebrew'], 
        word_desc['to_english_score'] / word_desc['to_english_attempts'])
  return word_desc
          
          
def play_to_hebrew_round(word_desc):
  if 'to_hebrew_score' not in word_desc or 'to_hebrew_attempts' not in word_desc:
      word_desc['to_hebrew_score'] = 0
      word_desc['to_hebrew_attempts'] = 0
  print('Translate ', word_desc['english'])
  answer = input()
  if answer == 'STOP_GAME':
      return None
  if similarity(answer, word_desc['hebrew']) > 0.8:
      print('Success: ', word_desc['hebrew'])
      word_desc['to_hebrew_score'] += 1
  else:
      print('Failure: ', word_desc['english'])
  play_hebrew_word(word_desc['hebrew'])
  word_desc['to_hebrew_attempts'] += 1
  print('Success rate for ', word_desc['hebrew'], 
          word_desc['to_hebrew_score'] / word_desc['to_hebrew_attempts'])
  return word_desc
      
      
  
filename = sys.argv[1] if len(sys.argv) > 1 and len(sys.argv[1]) > 0 else "common_words.json"
  
with open(filename) as common_words:
  words_list = json.load(common_words)
  random.shuffle(words_list)
  N = 20
  # We choose subset of N words and ask one of them repeatedly
  while True:
    word_id = random.randint(0, N - 1)
    word_desc = words_list[word_id]
    res = None
    if random.randint(0,1) == 1:
      res = play_to_english_round(word_desc)
      word_desc = res if res is not None else word_desc 
    else:
      res = play_to_hebrew_round(word_desc)
      word_desc = res if res is not None else word_desc  
    if res is None:
      break

  f = open(filename, "w")
  json.dump(words_list, f) 
  f.close()
