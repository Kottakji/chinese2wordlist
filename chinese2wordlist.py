#!/usr/bin/env python3

import re
import json
import argparse
from collections import defaultdict
from multiprocessing.dummy import Pool as ThreadPool
"""
Input chinese text to return a word list to use with learning
For example use python chinese2wordlist.py traditional 我是荷蘭人 
"""


class Chinese2WordList:

    character_type = None
    response_type = None
    language = None
    translated_dictionary_entries = defaultdict(list)
    smart_search_characters = defaultdict(list)
    search = []

    def __init__(self, chinese_text, character_type, response_type, language):
        self.character_type = character_type
        self.response_type = response_type
        self.language = language

        self._search_dictionary(chinese_text)

    def _search_dictionary(self, chinese_text):
        for key, character in enumerate(chinese_text):
            self._create_smart_search_list(key, character)

        self._search_dictionary_via_smart_search()

    def _create_smart_search_list(self, key, character):
        for items in list(self.smart_search_characters.items())[-3:]:
            tmp = list(items[1])
            tmp.append(items[1][-1] + character)
            self.smart_search_characters[items[0]] = tmp

        self.smart_search_characters[key].append(character)

    def _search_dictionary_via_smart_search(self):
        for items in self.smart_search_characters.items():
            pool = ThreadPool(4)
            result = pool.map(self._search_character_in_dictionary, items[1])
            self.translated_dictionary_entries[items[0]] = ([item for sublist in result if sublist for item in sublist if item])

    def _search_character_in_dictionary(self, character):

        if character in self.search:
            return None
        self.search.append(character)

        pattern = self._generate_search_regex(character)
        result = []
        with open(self._get_dictionary_location(), 'r') as dictionary:
            for line in dictionary:
                match = pattern.match(line)
                if match:
                    result.append(line)

        return result

    def _get_dictionary_location(self):
        if self.language == 'nl':
            return 'dictionary/cndict_1_0_ts_utf-8_mdbg.txt'

        return 'dictionary/cedict_1_0_ts_utf-8_mdbg.txt'

    def _generate_search_regex(self, character):
        pattern_string = self._get_character_type_regex()
        pattern = pattern_string.replace('character', character)

        return re.compile(pattern)

    def _extract_line_to_definitions(self, line):
        pattern = re.compile('(\S+)\s(\S+)\s\[(.+?)\]\s\/(.+)\/')
        match = pattern.match(line)
        traditional = match[1]
        simplified = match[2]
        pinyin = match[3]
        definition = match[4]
        return [traditional, simplified, pinyin, definition]

    def _get_character_type_regex(self):
        if self.character_type == 'traditional':
            return '(character) .+? \[.+?\] .+'
        return '.+? (character) \[.+?\] .+'

    def response(self):
        items = sorted(self.translated_dictionary_entries.items(), key=lambda item: item[0])
        values = [item[1] for item in items if item]
        if self.response_type in ['markdown', 'm']:
            return self._response_markdown(values)
        if self.response_type in ['json']:
            return self._response_json(values)

        return self.translated_dictionary_entries.items()

    def _response_json(self, values):
        return json.dumps(values)

    def _response_markdown(self, values):
        response = []

        for items in values:
            for item in items:
                traditional, simplified, pinyin, translation = self._extract_line_to_definitions(item)

                response.append("| {traditional} | {simplified} | {pinyin} | {translation} |".format(
                    simplified=simplified,
                    traditional=traditional,
                    pinyin=pinyin,
                    translation=translation
                ))

        return '\n'.join(response)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert Chinese text to a word list')
    parser.add_argument('chinese',
                        metavar='chinese',
                        help='chinese text')
    parser.add_argument('--character-input-type',
                        metavar='(traditional or simplified)',
                        default='simplified',
                        help='input type of the characters')
    parser.add_argument('--response-type',
                        metavar='json or markdown',
                        default='json',
                        help='return type')
    parser.add_argument('--language',
                        metavar='(en or nl)',
                        default='en',
                        help='language to translate to')

    args = parser.parse_args()

    chinese_word_list = Chinese2WordList(args.chinese, args.character_input_type, args.response_type, args.language)
    print(chinese_word_list.response())
