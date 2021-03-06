from difflib import SequenceMatcher
from typing import List, Dict
import json
import copy
import time
from collections import defaultdict

def equals_up_to_1(a: str, b: str) -> bool:
    similarity = SequenceMatcher(None, a, b).ratio()
    print(a, b, similarity)
    return similarity >= 1 - 1./max(len(a), len(b)) - 1e-4

def strip_parentheses(s: str) -> str:
    """
    Cleans up all parentheses contents of a string.
    """
    result = []
    inside = False
    for x in s:
        if x == '(':
            inside = True
        if not inside:
            result.append(x)
        if x == ')':
            inside = False
    return "".join(result)


class Word:
    """
    Represenets a word together with the learners stats.
    """

    def __init__(self, english: str, hebrew: str, translit: str):
        self.english = english.strip()
        self.hebrew = hebrew.strip()
        self.translit = translit
        # Numbers of total attempts
        self.e2h_attempts = 0
        self.h2e_attempts = 0
        # Numbers of successful attempts
        self.e2h_success = 0
        self.h2e_success = 0
        # The lists of failed attempts
        self.e2h_failures = []
        self.h2e_failures = []
        # Successes timestamps (in seconds, time.ctime())
        self.e2h_success_timespamps = []
        self.h2e_success_timestamps = []

    def join(self, another: 'Word') -> bool:
        if self.english != another.english:
            return False
        self.e2h_attempts += another.e2h_attempts
        self.h2e_attempts += another.h2e_attempts
        self.e2h_success += another.e2h_success
        self.h2e_success += another.h2e_success
        self.e2h_failures += another.e2h_failures
        self.h2e_failures += another.h2e_failures
        self.e2h_success_timestamps += another.e2h_success_timestamps
        self.h2e_success_timestamps += another.h2e_success_timestamps
        

    def hebrew_correct(self, attempt: str):
        attempt = attempt.strip()
        return equals_up_to_1(attempt, self.hebrew)

    def english_correct(self, attempt: str):
        attempt = attempt.strip()
        return equals_up_to_1(attempt.lower(), strip_parentheses(self.english.lower()))

    def make_hebrew_attempt(self, attempt: str):
        self.e2h_attempts += 1
        if self.hebrew_correct(attempt):
            self.e2h_success += 1
            self.e2h_success_timestamps.append(time.ctime())
            return True
        self.e2h_failures.append(attempt)
        return False
    
    def make_english_attempt(self, attempt: str):
        self.h2e_attempts += 1
        if self.english_correct(attempt):
            print(self.h2e_success)
            self.h2e_success += 1
            self.h2e_success_timestamps.append(time.ctime())
            return True
        self.h2e_failures.append(attempt)
        return False  

    @staticmethod
    def from_json(description: dict):
        word_obj = Word(description['english'], description['hebrew'], description['translit'])
        
        word_obj.e2h_attempts = description.get('english_to_hebrew_attempts', 0)
        word_obj.h2e_attempts = description.get('hebrew_to_english_attempts', 0)
        word_obj.e2h_success = description.get('english_to_hebrew_success', 0)
        word_obj.h2e_success = description.get('hebrew_to_english_success', 0)
        word_obj.e2h_failures = description.get('english_to_hebrew_failures', [])
        word_obj.h2e_failures = description.get('hebrew_to_english_failures', [])
        word_obj.e2h_success_timestamps = description.get('english_to_hebrew_success_timestamps', [])
        word_obj.h2e_success_timestamps = description.get('hebrew_to_english_success_timestamps', [])
        
        return word_obj        
        
        

class WordJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Word):
            return {"english": obj.english,
                    "hebrew": obj.hebrew,
                    "translit": obj.translit,
                    "english_to_hebrew_attempts": obj.e2h_attempts,
                    "hebrew_to_english_attempts": obj.h2e_attempts,
                    "english_to_hebrew_success": obj.e2h_success,
                    "hebrew_to_english_success": obj.h2e_success,                    
                    "english_to_hebrew_failures": copy.deepcopy(obj.e2h_failures),
                    "hebrew_to_english_failures": copy.deepcopy(obj.h2e_failures),
                    "english_to_hebrew_success_timestamps": obj.e2h_success_timestamps,
                    "hebrew_to_english_success_timestamps": obj.h2e_success_timestamps,                    
                    }
        return json.JSONEncoder.default(self, obj)


def join_two_wordlists(list1: List[Word], list2: List[Word]) -> List[Word]:
    d: Dict[str, List[Word]] = defaultdict(list)
    for w in list1 + list2:
        d[w.english].append(w)
    result = []
    for key, value in d.items():
        if len(value) == 0:
            continue
        joint_word = value[0]
        for w in value[1:]:
            joint_word.join(w)
        result.append(joint_word)
    return result
    
