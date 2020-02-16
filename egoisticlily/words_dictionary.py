# -*- coding: utf-8 -*-
"""
 Copyright (c) 2020 Masahiko Hashimoto <hashimom@geeko.jp>

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
import os
import csv
import glob
import random
import pickle
import marisa_trie


class WordsDictionary:
    def __init__(self):
        self.surface_trie = None
        self.reads_trie = None
        self.words_dic_info = []

    def rebuild_trie(self):
        trie_surface_keys = []
        trie_reads_keys = []
        trie_values = []

        for i, word in enumerate(self.words_dic_info):
            trie_surface_keys.append(word["surface"])
            trie_reads_keys.append(word["read"])
            trie_values.append([i])

        self.surface_trie = marisa_trie.RecordTrie("<I", zip(trie_surface_keys, trie_values))
        self.reads_trie = marisa_trie.RecordTrie("<I", zip(trie_reads_keys, trie_values))

    def get_from_surface(self, key):
        word_id = None
        if key in self.surface_trie:
            word_id = self.surface_trie[key]
        return word_id

    def get_from_read(self, key):
        word_id = None
        if key in self.reads_trie:
            word_id = self.reads_trie[key]
        return word_id

    def get_from_id(self, word_id):
        return self.words_dic_info[word_id]

    def save(self, out_path):
        """ 単語情報save

        :param out_path:
        :return:
        """
        with open(out_path, "wb") as f:
            pickle.dump(self.words_dic_info, f)


class WordsDictionaryFromMecab(WordsDictionary):
    def __init__(self):
        """ 辞書 (for Train)

        """
        super(WordsDictionaryFromMecab, self).__init__()
        self.surfaces = {}
        self.ids = []
        self.pos_id = {}

    def read_meacab_dic(self, in_mecab_dir):
        """ Mecabから辞書を作成

        :param in_mecab_dir:
        """
        mecab_dir = os.path.abspath(in_mecab_dir)

        # Pos_ID リスト取得
        with open(mecab_dir + "/pos-id.def", "r") as f:
            reader = csv.reader(f, delimiter=" ")
            for row in reader:
                self.pos_id[row[0]] = row[1]

        # 辞書初期化
        for csv_file in glob.glob(mecab_dir + "/*.csv"):
            with open(csv_file, "r") as f:
                try:
                    reader = csv.reader(f, delimiter=",")
                    for i, row in enumerate(reader):
                        word_id = self.reg_word(row[0], row[9], row[4], row[5])
                        if word_id is None:
                            print("[word reg err] %s (not found pos_id)" % row[0])
                            continue

                except Exception as e:
                    print("[words reg err] %s: " % row[0], e)
                    continue

    def reg_word(self, surface, read, pos_id_1, pos_id_2):
        """ 単語登録

        :param surface:
        :param read:
        :param pos_id_1:
        :param pos_id_2:
        :return:
        """
        word_id = None
        pos_id = None

        # pos_id 取得
        pos_id_str = pos_id_1 + "," + pos_id_2
        if pos_id_str in self.pos_id:
            pos_id = self.pos_id[pos_id_str]

        # 単語登録
        if pos_id is not None:
            word_id = len(self.words_dic_info)
            self.words_dic_info.append({"vec_id": random.random(),
                                        "surface": surface,
                                        "read": read,
                                        "pos_id": pos_id})
            self.surfaces[surface] = word_id

        return word_id

    def get_word_id(self, key):
        """ 単語列から単語ID取得

        :param key:
        :return:
        """
        word_id = None
        if key in self.surfaces:
            word_id = self.surfaces[key]
        return word_id


class WordsDictionaryTrain(WordsDictionary):
    def __init__(self, in_pkl_file):
        super(WordsDictionaryTrain, self).__init__()
        with open(in_pkl_file, 'rb') as f:
            self.words_dic_info = pickle.load(f)

        self.rebuild_trie()


