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
import argparse
import pickle
from tqdm import tqdm
from egoisticlily.words_dictionary import WordsDictionaryFromMecab


class Parser:
    def __init__(self, out_path, mecab_dic_path):
        """ 解析

        :param out_path: 出力パス (directory)
        :param mecab_dic_path: Mecabパス (directory)
        """
        self.word_dic = WordsDictionaryFromMecab()
        self.word_dic.read_meacab_dic(mecab_dic_path)

        # 出力配置ディレクトリ生成
        self.out_path = out_path
        self.out_data_path = out_path + "/data/"
        if not os.path.isdir(self.out_data_path):
            os.makedirs(self.out_data_path)

    def __call__(self, in_file):
        """

        :param in_file: 入力ファイル
        :return:
        """
        base, _ = os.path.splitext(os.path.basename(in_file))
        self.in_file = in_file
        self.out_file = self.out_data_path + base

        bodies = []
        link_info = []
        with open(self.in_file) as f:
            for line in f.readlines():
                line_split = line.split()

                # 文
                if line_split[0] == "#":
                    body = []
                    link_info_body = []
                    chunk = None

                # 文節
                elif line_split[0] == "*":
                    if chunk is not None:
                        body.append(chunk)
                    chunk = []

                    # 係り受け情報登録
                    link_info_body.append(int(line_split[1][:-1]))

                # 補足？
                elif line_split[0] == "+":
                    pass

                # 文末
                elif line_split[0] == "EOS":
                    body.append(chunk)
                    bodies.append(body)
                    link_info.append(link_info_body)

                # 単語
                else:
                    word_id = self.word_dic.get_word_id(line_split[0])
                    if word_id is None:
                        # 見つからなかった場合は単語を新規登録
                        word_id = self.word_dic.reg_word(line_split[0], line_split[1], line_split[3], line_split[5])

                    chunk.append(word_id)

        output = []
        for body_idx, body in enumerate(bodies):
            # 文節内前後の単語登録
            for chunk in body:
                for i, word_id in enumerate(chunk):
                    # 文節先頭の単語は無視
                    if i != 0:
                        pre_word = chunk[i-1]
                        output.append([pre_word, word_id])

            # 係り受け前後の単語登録
            #for i, link in enumerate(link_info[body_idx]):
            #    pre_word = body[i][-1]
            #    word_id = body[link][0]
            #    output.append([pre_word, word_id])

        # save
        with open(self.out_file + ".pkl", "wb") as f:
            pickle.dump(output, f)

    def save_dic_info(self):
        """ 単語情報 save

        :return:
        """
        self.word_dic.save(self.out_path + "/words_dat.pkl")


def main():
    """ main

    :return:
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i', '--in_path', help='KWDLC path', required=True)
    arg_parser.add_argument('-t', '--in_type', help='Input Type ("train" or "test" or "all")', default="all")
    arg_parser.add_argument('-o', '--out_path', help='output path', default="in/")
    arg_parser.add_argument('-m', '--mecab_dic_path', help='Mecab Dic path', required=True)
    args = arg_parser.parse_args()

    out_path = os.path.abspath(args.out_path)
    if not os.path.isdir(out_path):
        os.makedirs(out_path)

    # リスト作成
    in_file_list = []
    if args.in_type != "test":
        # 学習用ファイルリスト追加
        with open(os.path.abspath(args.in_path + "/train.files")) as f:
            for file in f.readlines():
                in_file_list.append(file.rstrip('\n'))
    if args.in_type != "train":
        # テスト用ファイルリスト追加
        with open(os.path.abspath(args.in_path + "/test.files")) as f:
            for file in f.readlines():
                in_file_list.append(file.rstrip('\n'))

    # 解析
    parser = Parser(out_path, args.mecab_dic_path)
    for file in tqdm(in_file_list):
        parser(os.path.abspath(args.in_path + "/" + file))

    # 単語情報save
    parser.save_dic_info()


if __name__ == "__main__":
    main()
