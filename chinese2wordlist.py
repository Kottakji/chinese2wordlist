#!/usr/bin/env python3
import sys
from enum import Enum
import re
from collections import defaultdict

"""
Input chinese text to return a word list to use with learning
For example use python chinese2wordlist.py traditional 我是荷蘭人 
"""


class Chinese2WordList:

    character_type = None
    translated_dictionary_entries = defaultdict(list)
    smart_search_characters = defaultdict(list)

    def __init__(self, character_type, chinese_text):
        self.character_type = character_type

        self.search_dictionary(chinese_text)
        self.return_word_list()

    def search_dictionary(self, chinese_text):
        for key, character in enumerate(chinese_text):
            self._create_smart_search_list(key, character)

        self._search_dictionary_via_smart_search()

    def _create_smart_search_list(self, key, character):
        for items in list(self.smart_search_characters.items()):
            tmp = list(items[1])
            tmp.append(items[1][-1] + character)
            self.smart_search_characters[items[0]] = tmp

        self.smart_search_characters[key].append(character)

    def _search_dictionary_via_smart_search(self):
        for items in self.smart_search_characters.items():
            for character in items[1]:
                self._search_character_in_dictionary(items[0], character)

    def _search_character_in_dictionary(self, key, character):
        pattern = self._generate_search_regex(character)

        with open('dictionary/cedict_1_0_ts_utf-8_mdbg.txt', 'r') as dictionary:
            for line in dictionary:
                result = pattern.match(line)
                if result:
                    self.translated_dictionary_entries[key].append(line)

    def _generate_search_regex(self, character):
        pattern_string = self.character_type.value
        pattern = pattern_string.replace('character', character)

        return re.compile(pattern)

    def return_word_list(self):
        for entry in self.translated_dictionary_entries.items():
            print(entry)


class CharacterType(Enum):
    """
    Select between Traditional or Simplified and get the correct regex to use for searching
    """
    TRADITIONAL = '(character) .+? \[.+?\] .+'
    SIMPLIFIED = '.+? (character) \[.+?\] .+'


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print('Incorrect arguments')
        print('Specify if you want simplified or traditional characters and input chinese text')
        print('For simplified: chinese2wordlist.py s 我')
        print('For traditional: chinese2wordlist.py t 我')
        exit()

    if sys.argv[1] in ['t', 'trad', 'traditional']:
        Chinese2WordList(CharacterType.TRADITIONAL, sys.argv[2])
    elif sys.argv[1] in ['s', 'simp', 'simplified']:
        Chinese2WordList(CharacterType.SIMPLIFIED, sys.argv[2])
    else:
        print('Wrong character type:', sys.argv[1])
        exit()
