import gtts
from playsound import playsound
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