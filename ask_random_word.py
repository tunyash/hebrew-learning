from pywebio.input import input, FLOAT
from pywebio.output import put_text, clear, toast, put_markdown, put_scope,\
                           use_scope, put_table, put_button, put_collapse, put_link
import gtts
from playsound import playsound
import json
import random
import sys
from word import Word, WordJSONEncoder
import copy
import os.path
import base64

def play_hebrew_word(word):
  word_code = str(base64.b64encode(word.encode('utf-8')))
  if os.path.isfile('sounds/' + word_code + ".mp3"):
    playsound('sounds/' + word_code + ".mp3")
    return
  tts = gtts.gTTS(word, lang="iw")
  print(word, word_code)
  tts.save('sounds/' + word_code + ".mp3")
  playsound('sounds/' + word_code + ".mp3")

def make_word_play_lambda(word):
  def func():
    play_hebrew_word(word)
  return func
  
def play_to_english_round(word: Word):
  play_hebrew_word(word.hebrew)
  answer = input('Translate ' + word.hebrew)
  if answer == 'STOP_GAME':
    return None
  result = word.make_english_attempt(answer)
  use_scope('results')
  clear()
  if result:
    toast('Success!')
    put_markdown("**Correct**: *" + word.hebrew.strip() + "* is *" + word.english.strip() + "*")
  else:
    toast('Fail!')
    put_markdown("**Incorrect**: *" + answer.strip() + "* is *not* *" + word.english.strip() + "*")
  return word
          
          
def play_to_hebrew_round(word: Word):
  answer = input('Translate ' + word.english)
  if answer == 'STOP_GAME':
      return None
  result = word.make_hebrew_attempt(answer)
  use_scope('results')
  clear()
  if result:
    toast('Success!')
    put_markdown("**Correct**: *" + word.english + "* is *" + word.hebrew + "*")
  else:
    toast('Fail!')
    put_markdown("**Incorrect**: *" + answer + "* is not *" + word.hebrew + "*")
  play_hebrew_word(word.hebrew)   
  return word
      
      
  
filename = sys.argv[1] if len(sys.argv) > 1 and len(sys.argv[1]) > 0 else "common_words.json"
  
put_scope('results')
put_scope('worst_words')
put_scope('question')

with open(filename) as common_words:
  # We choose subset of N words and ask one of them repeatedly
  N = int(input('Type in the number of words you would like to study'))
  words_list = [Word.from_json(desc) for desc in json.load(common_words)]
  random.shuffle(words_list)

  put_table(tdata=[[put_button(word.english, 
                               onclick=make_word_play_lambda(word.hebrew)),
                    word.hebrew + '(' + word.translit + ')'] for word in words_list[:N]],
            header=['English', 'Hebrew'])
  
  
  while True:
    use_scope('question')
    word_id = min(N-1, int(random.expovariate(N/2.)))
    word_desc = words_list[word_id]
    res = None
    alpha_h2e = word_desc.h2e_success/(1.+word_desc.h2e_attempts) 
    alpha_e2h = word_desc.e2h_success/(1.+word_desc.e2h_attempts) 
    if random.random() >= (alpha_h2e + .25)/(alpha_e2h + alpha_h2e + .5):
      res = play_to_english_round(word_desc)
      word_desc = res if res is not None else word_desc 
    else:
      res = play_to_hebrew_round(word_desc)
      word_desc = res if res is not None else word_desc  
    if res is None:
      break

    use_scope('worst_words')
    words_by_success = sorted(words_list[:N], key=lambda x: x.h2e_success/(1.+x.h2e_attempts) + 
                                                            x.e2h_success/(1.+x.e2h_attempts))
    for i in range(N):
      words_list[i] = words_by_success[i]
    put_collapse(title='Word list', 
                 content=[
                   put_table(tdata=[[put_button(word.english, 
                                                onclick=make_word_play_lambda(word.hebrew)),
                    word.hebrew + '(' + word.translit + ')',
                    str(word.e2h_success) + '/' + str(word.e2h_attempts),
                    str(word.h2e_success) + '/' + str(word.h2e_attempts),
                    put_link(name='Context',
                             url='https://context.reverso.net/translation/hebrew-english/' + word.hebrew, 
                             new_window=True)] for word in words_by_success],
            header=['English', 'Hebrew', 'English2Hebrew', 'Hebrew2English', 'Context'])],
            open=False)                                                        

    f = open(filename, "w")
    json.dump(words_list, f, cls=WordJSONEncoder, indent=4) 
    f.close()
