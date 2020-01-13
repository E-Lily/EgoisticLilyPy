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
import csv
import argparse
import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from egoisticlily.modelmaker.wordvector import CostAeModel
from egoisticlily.modelmaker.wordholder import WordHolder

WORD_PHRASE_NUM = 4
WORD_ID_BIT_NUM = 16


class Builder:
    def __init__(self, word_file, link_file, output_dir):
        """ モデル生成

        :param word_file:
        :param link_file:
        :param output_dir:
        """
        # DNN define
        hid_dim = 64
        z_dim = 16
        hid_num = 1

        # モデル生成用辞書ファイル読み込み
        self.word_holder = WordHolder(word_file)
        type1_cnt, type2_cnt = self.word_holder.type_list_cnt()
        self.link_list = []
        with open(link_file, encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=",")
            for row in reader:
                self.link_list.append(row)

        # モデル配置ディレクトリ生成
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        self.out_dir = output_dir

        self.model = CostAeModel(type1_cnt, type2_cnt, hid_dim, z_dim, hid_num, WORD_ID_BIT_NUM, WORD_PHRASE_NUM)

    def __call__(self, epoch_num, batch_size):
        """ 学習実行

        :param epoch_num:
        :param batch_size:
        :return:
        """
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)

        # 学習開始
        self.model.train()
        for i in range(epoch_num):
            # バッチリスト生成 ※ゆくゆくはデータセットへ移行する予定
            batch_list = []
            rand_list = np.random.randint(0, len(self.link_list), batch_size)
            for rand_i in rand_list:
                batch_list.append(self.link_list[rand_i])
            batch = self.make_batch(batch_list, batch_size)
            x_list = torch.from_numpy(batch)

            # 学習データを入力して損失値を取得
            y = self.model(x_list)
            loss = criterion(y, x_list)

            # 勾配を初期化してBackProp
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            print("[%d] loss: %f" % (i, loss))

            # １エポック毎に単語ベクトルを更新している
            self.update_word_id(batch_list, y)

        self.word_holder.save(self.out_dir)
        torch.save(self.model.state_dict(), self.out_dir + "/dnn.mdl")

    def make_batch(self, batch_list, batch_size):
        """　バッチ生成 ※将来的にデータセットへ移行する

        :param batch_list:
        :param batch_size:
        :return:
        """
        # 4単語×80 = 320決め打ちになってしまってる ※後で直す
        batch = np.empty((batch_size, 320), dtype="float32")
        for i, x in enumerate(batch_list):
            word_id = np.empty((WORD_PHRASE_NUM, 80), dtype="float32")
            for j in range(WORD_PHRASE_NUM):
                if not x[j] in self.word_holder.word_list:
                    self.word_holder.regist(x[j], x[j], "未定義語", "その他")
                word_id[j] = self.word_holder(x[j])
            batch[i] = word_id.reshape(1, 320)
        return batch

    def update_word_id(self, batch_list, y):
        """ 係り受け表現から単語Vectorを求めそれを反映する

        :param batch_list:
        :param y:
        :return:
        """
        for i, link in enumerate(batch_list):
            y_word_ary = torch.reshape(y[i], (WORD_PHRASE_NUM, 80))
            for j, word in enumerate(link):
                new_id = 0
                y_word = y_word_ary[j][:WORD_ID_BIT_NUM]
                # この辺りいい加減・・・（ようは平均以上の値にたいしてフラグを立てている）
                y_mean = torch.mean(y_word)
                for val in y_word:
                    if val > y_mean:
                        new_id += 1
                    new_id = new_id << 1
                self.word_holder.word_list[word]["vec_id"] = int(new_id)


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-l', nargs='?', help='input link file', required=True)
    arg_parser.add_argument('-w', nargs='?', help='input word file', required=True)
    arg_parser.add_argument('-o', nargs='?', help='output model directory', required=True)
    args = arg_parser.parse_args()

    builder = Builder(args.w, args.l, args.o)
    builder(200, 500)


if __name__ == "__main__":
    main()



