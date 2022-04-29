import csv
import json 
import sys

filename = sys.argv[1] if len(sys.argv) > 1 and len(sys.argv[1]) > 0 else "common_words.csv"

result = []

with open(filename) as csv_file:
  reader = csv.reader(csv_file, delimiter=',')
  category = ""
  for row in reader:
    if row[0] != '':
      category = row[0]
      continue
    word_desc = dict()
    word_desc['english'] = row[1]
    word_desc['hebrew'] = row[3]
    word_desc['category'] = category
    word_desc['translit'] = row[2]
    print(word_desc)
    result.append(word_desc)
    
f = open(filename.split('.')[0] + ".json", "w")
json.dump(result, f, indent=4)
f.close()
