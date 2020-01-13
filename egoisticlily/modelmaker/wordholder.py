# -*- coding: utf-8 -*-
"""
 Copyright (c) 2019 Masahiko Hashimoto <hashimom@geeko.jp>

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
"""
import csv
import marisa_trie
import numpy as np
from egoisticlily.words import Words


class WordHolder:
    def __init__(self, list_file=None):
        self.word_list = {}
        self.words_info = Words()

        # word file read
        if list_file is not None:
            with open(list_file, "r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter=",")
                for row in reader:
                    self.word_list[row[0]] = {"read": row[1], "vec_id": row[2], "type1": row[3], "type2": row[4]}

    def __call__(self, surface):
        return self.words_info(int(self.word_list[surface]["vec_id"]),
                               int(self.word_list[surface]["type1"]),
                               int(self.word_list[surface]["type2"]))

    def regist(self, surface, read, type1, type2):
        if not surface in self.word_list:
            vec_id = np.random.randint(0, 65535)
            if type2 != "*":
                self.word_list[surface] = {"vec_id": vec_id,
                                           "read": read,
                                           "type1": self.words_info.word_type_list[0].index(type1),
                                           "type2": self.words_info.word_type_list[1].index(type2)}
            else:
                self.word_list[surface] = {"vec_id": vec_id,
                                           "read": read,
                                           "type1": self.words_info.word_type_list[0].index(type1),
                                           "type2": self.words_info.word_type_list[0].index(type1)}

    def save(self, out_dir):
        with open(out_dir + "/words.csv", 'w', encoding="utf-8") as f:
            writer = csv.writer(f, lineterminator='\n')
            trie_keys = []
            trie_values = []
            for i, [k, v] in enumerate(self.word_list.items()):
                writer.writerow([k, v["read"], v["vec_id"], v["type1"], v["type2"]])
                trie_keys.append(v["read"])
                trie_values.append([i, int(v["vec_id"]), int(v["type1"]), int(v["type2"])])

        trie = marisa_trie.RecordTrie("<IIHH", zip(trie_keys, trie_values))
        trie.save(out_dir + '/words.marisa')

    def type_list_cnt(self):
        return [len(self.words_info.word_type_list[0]), len(self.words_info.word_type_list[1])]


