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
import os
import json
import csv
import glob
from egoisticlily.modelmaker.wordholder import WordHolder


class PreBuilder:
    def __init__(self, in_dir, out_dir):
        """ モデルビルド用CSVファイル作成（pre処理）

        :param in_dir:
        :param out_dir:
        """
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)
        self.out_dir = out_dir
        self.in_dir = in_dir

        if os.path.isfile(out_dir + "/words.csv"):
            self.word_holder = WordHolder(out_dir + "/words.csv")
        else:
            self.word_holder = WordHolder()
        type_cnt = self.word_holder.type_list_cnt()
        self.soc_type = type_cnt
        self.eoc_type = [type_cnt[0], type_cnt[1]+1]
        self.non_type = [type_cnt[0], type_cnt[1]+2]

    def __call__(self):
        """ モデルビルド用CSVファイル作成

        :return:
        """
        with open(self.out_dir + "/word_link.csv", 'w', encoding="utf-8") as f:
            writer = csv.writer(f, lineterminator='\n')
            file_list = glob.glob(self.in_dir + "/*.json")
            for file in file_list:
                with open(file, encoding="utf-8") as in_json:
                    info = json.load(in_json)
                    link_info = {}

                    # Word info
                    for chunk in info["Chunks"]:
                        words = chunk["Independent"] + chunk["Ancillary"]
                        for word in words:
                            self.word_holder.regist(word["surface"], word["read"],
                                                    word["position"][0], word["position"][1])

                    # Link info
                    for chunk in info["Chunks"]:
                        if len(chunk["Independent"]) == 1 and not chunk["Link"] is None:
                            link_info.update(self.make_link_info(chunk))

                    for chunk in info["Chunks"]:
                        # Word info
                        word_info = self.make_word_info(chunk, link_info)
                        # CSV write
                        for link in word_info:
                            writer.writerow(link)

        self.word_holder.save(self.out_dir)

    @staticmethod
    def make_word_info(chunk, link_info):
        """ bi-gram情報生成

        :param chunk:
        :param link_info:
        :return:
        """
        bigram_list = []
        word_info_list = []
        words = chunk["Independent"] + chunk["Ancillary"]
        chunk_len = len(words)
        if chunk_len != 0:
            if chunk_len == 1:
                bigram_list.append({"pre": "@S@", "post": words[0]["surface"]})
                bigram_list.append({"pre": words[0]["surface"], "post": "@E@"})
            else:
                for i, word in enumerate(words):
                    bi_word = {}
                    if i == 0:
                        bi_word["pre"] = "@S@"
                    else:
                        bi_word["pre"] = words[i - 1]["surface"]

                    bi_word["post"] = word["surface"]
                    bigram_list.append(bi_word)

                    if i == (chunk_len - 1):
                        bigram_list.append({"pre": word["surface"], "post": "@E@"})

            for bi_gram in bigram_list:
                link = ["@N@", "@N@"]
                if bi_gram["post"] in link_info:
                    link = link_info[bi_gram["post"]]
                word_info_list.append(link + [bi_gram["pre"], bi_gram["post"]])

        return word_info_list

    def make_link_info(self, chunk):
        """ 係り受け情報生成

        :param chunk:
        :return:
        """
        ind_phase = ""
        ind_read = ""
        lnk_phase = ""
        lnk_read = ""
        # lnk_org = ""

        # Independent
        if len(chunk["Independent"]) == 1:
            ind_phase = chunk["Independent"][0]["surface"]
        else:
            for independent in chunk["Independent"]:
                ind_phase += independent["surface"]
                ind_read += independent["read"]
            self.word_holder.regist(ind_phase, ind_read, "未定義語", "その他")

        # Ancillary
        if len(chunk["Ancillary"]) == 1 and chunk["Ancillary"][0]["position"][0] != "特殊":
            anc_phase = chunk["Ancillary"][0]["surface"]
        else:
            anc_phase = "@N@"

        # Link
        if len(chunk["Ancillary"]) == 1:
            lnk_phase = chunk["Link"][0]["surface"]
            # lnk_org = chunk["Link"][0]["original"]
        else:
            for i, link in enumerate(chunk["Link"]):
                if i == 0:
                    if link["position"][0] == "動詞" or link["position"][0] == "形容詞":
                        lnk_phase = link["surface"]
                        # lnk_org = link["original"]
                        lnk_read = link["read"]
                        break
                lnk_phase += link["surface"]
                # lnk_org += link["original"]
                lnk_read += link["read"]
            self.word_holder.regist(lnk_phase, lnk_read, "未定義語", "その他")
            # self.word_holder.regist(lnk_org, "未定義語", "その他")

        return {lnk_phase: [ind_phase, anc_phase]}


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i', nargs='?', help='input json file path', required=True)
    arg_parser.add_argument('-o', nargs='?', help='output directory name', required=True)
    args = arg_parser.parse_args()

    builder = PreBuilder(args.i, args.o)
    builder()


if __name__ == "__main__":
    main()
