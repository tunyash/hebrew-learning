from difflib import SequenceMatcher
import gtts
from playsound import playsound
import json
import random

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def play_hebrew_word(word):
  tts = gtts.gTTS(word, lang="iw")
  tts.save("sound.mp3")
  playsound("sound.mp3")
    
  
with open("common_words.json") as common_words:
  words_list = json.load(common_words)
  random.shuffle(words_list)
  N = 20
  # We choose subset of N words and ask one of them repeatedly
  while True:
    word_id = random.randint(0, N - 1)
    word_desc = words_list[word_id]
    if 'to_english_score' not in word_desc or 'to_english_attempts' not in word_desc:
      word_desc['to_english_score'] = 0
      word_desc['to_english_attempts'] = 0
    print('Translate ', word_desc['hebrew'], '(' + word_desc['translit'] + ')')
    play_hebrew_word(word_desc['hebrew'])
    answer = input()
    if answer == 'STOP_GAME':
      break
    if any(similarity(answer, word) > 0.8 for word in word_desc['english'].split()):
      print('Success: ', word_desc['english'])
      word_desc['to_english_score'] += 1
    else:
      print('Fail, correct words: ', word_desc['english'])
    word_desc['to_english_attempts'] += 1
    print('Success rate for ', word_desc['hebrew'], 
          word_desc['to_english_score'] / word_desc['to_english_attempts'])

f = open("common_words.json", "w")
json.dump(words_list, f)
f.close()
