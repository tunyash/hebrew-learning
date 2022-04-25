import json

with open("common_words.json") as common_words:
  words_list = json.load(common_words)
  words_list = sorted(words_list, 
                      key=lambda x: 
                        0 if 'to_english_attempts' not in x 
                        else -x['to_english_attempts'])
  for word in words_list:
    print(word['english'], word['hebrew'], word['translit'], sep=',')
