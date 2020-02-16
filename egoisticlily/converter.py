# -*- coding: utf-8 -*-
"""
 Copyright (c) 2019-2020 Masahiko Hashimoto <hashimom@geeko.jp>

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
import argparse
import numpy as np
import torch
import torch.nn as nn
from egoisticlily.words_dictionary import WordsDictionaryTrain
from egoisticlily.model import ELilyModel


class Converter:
    def __init__(self, model_dir, pos_id_num=43):
        """ 変換モジュール

        :param model_dir:
        """
        self.words = []
        self.loss = nn.MSELoss()

        self.word_info = WordsDictionaryTrain(model_dir + "/words_dat.pkl")
        self.model = ELilyModel()
        self.model.load_state_dict(torch.load(model_dir + "/elily.mdl"))
        self.pos_id_one_hot = np.eye(pos_id_num, dtype="float32")

    def __call__(self, in_text):
        """ 変換

        :param in_text:
        :return:
        """
        # init_id = self.id_list("@S@")[0]

        # words_set build
        words_set = [[] for i in range(len(in_text))]
        for i in range(len(in_text)):
            for prefix in self.word_info.reads_trie.prefixes(in_text[i:]):
                words_set[i+len(prefix)-1].append(prefix)

        # node build
        min_node = []
        for i in range(len(words_set)):
            min_node.append({"cost": 0., "id": -1, "con_idx": 0})

            for node_read in words_set[i]:
                node_read_len = len(node_read)
                con_index = i - node_read_len
                for node_one in self.id_list(node_read):
                    if con_index < 0:
                        cost_tmp = 1.
                    else:
                        score_tmp = self.score(min_node[con_index]["id"], node_one)
                        cost_tmp = min_node[con_index]["cost"] + score_tmp
                    print("[%d]    %s: %f" % (i, self.word_info.words_dic_info[node_one]["surface"], cost_tmp))

                    if cost_tmp < min_node[i]["cost"] or min_node[i]["cost"] == 0.:
                        min_node[i]["cost"] = cost_tmp
                        min_node[i]["id"] = node_one
                        min_node[i]["con_idx"] = con_index
                        print("[%d] -> %s: %f" % (i, self.word_info.words_dic_info[node_one]["surface"], cost_tmp))

        node_idx_ary = []
        node_idx = len(words_set) - 1
        for i in range(len(words_set)):
            node_idx_ary.append(node_idx)
            node_idx = min_node[node_idx]["con_idx"]
            if node_idx < 0:
                node_idx_ary.reverse()
                break

        ret_str = ""
        for i in node_idx_ary:
            ret_str += self.word_info.words_dic_info[min_node[i]["id"]]["surface"]
        return ret_str

    def score(self, word1_id, word2_id):
        """ スコア取得

        :param word1_id:
        :param word2_id:
        :return:
        """
        pre_word = self.word_info.get_from_id(word1_id)
        post_word = self.word_info.get_from_id(word2_id)

        pre_vec_id = np.array(pre_word["vec_id"], dtype="float32")
        post_vec_id = np.array(post_word["vec_id"], dtype="float32")

        vec = np.hstack((pre_vec_id, post_vec_id))
        vec = np.hstack((vec, self.pos_id_one_hot[int(pre_word["pos_id"])]))
        vec = np.hstack((vec, self.pos_id_one_hot[int(post_word["pos_id"])]))
        vec = torch.from_numpy(vec)
        y = self.model(vec)
        return self.loss(y, vec)

    def id_list(self, word):
        """ TrieIDリスト取得

        :param word:
        :return:
        """
        ret = []
        for word_id in self.word_info.reads_trie.get(word):
            ret.append(word_id[0])
        return ret


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-m', nargs='?', help='output directory name', required=True)
    arg_parser.add_argument('-t', nargs='?', help='pre', required=True)
    args = arg_parser.parse_args()

    converter = Converter(args.m)
    ret = converter(args.t)
    print(ret)


if __name__ == "__main__":
    main()


