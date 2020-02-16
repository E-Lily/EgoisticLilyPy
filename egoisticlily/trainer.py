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
import argparse
import os
import numpy as np
import glob
import pickle
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm
from torch.utils.data import Dataset
from egoisticlily.model import ELilyModel
from egoisticlily.words_dictionary import WordsDictionaryTrain


class ELilyDataSets(Dataset):
    def __init__(self, in_path, word_info, transform=None, pos_id_num=43):
        self.transform = transform
        self.word_info = word_info
        self.pos_id_one_hot = np.eye(pos_id_num, dtype="float32")

        self.word_id_pre_list = []
        self.word_id_post_list = []

        file_list = glob.glob(os.path.abspath(in_path) + "/data/*.pkl")
        for file in file_list:
            with open(file, 'rb') as f:
                pkl_data = pickle.load(f)
                for data in pkl_data:
                    if data[0] is not None and data[1] is not None:
                        self.word_id_pre_list.append(data[0])
                        self.word_id_post_list.append(data[1])

    def __len__(self):
        return len(self.word_id_pre_list)

    def __getitem__(self, idx):
        pre_word = self.word_info.get_from_id(self.word_id_pre_list[idx])
        post_word = self.word_info.get_from_id(self.word_id_post_list[idx])

        pre_vec_id = np.array(pre_word["vec_id"], dtype="float32")
        post_vec_id = np.array(post_word["vec_id"], dtype="float32")

        vec = np.hstack((pre_vec_id, post_vec_id))
        vec = np.hstack((vec, self.pos_id_one_hot[int(pre_word["pos_id"])]))
        vec = np.hstack((vec, self.pos_id_one_hot[int(post_word["pos_id"])]))
        return vec, self.word_id_pre_list[idx], self.word_id_post_list[idx]


class Trainer:
    def __init__(self, in_path, out_path):
        self.word_info = WordsDictionaryTrain(in_path + "/words_dat.pkl")
        self.out_path = out_path
        self.data_set = ELilyDataSets(in_path, self.word_info)
        self.model = ELilyModel()

        self.use_device = "cpu"
        if torch.cuda.is_available():
            self.use_device = "cuda"
            self.model.to(self.use_device)

    def __call__(self, epoch_num, batch_size):
        """ 学習実行

        :param epoch_num:
        :param batch_size:
        :return:
        """
        train_loader = torch.utils.data.DataLoader(self.data_set,
                                                   batch_size=batch_size,
                                                   shuffle=True,
                                                   num_workers=2)
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)

        # 学習開始
        self.model.train()
        bar = tqdm(range(epoch_num))
        for _ in bar:
            batch_loss = 0.
            for vec, pre_id, post_id in train_loader:
                x_in = vec.to(self.use_device)
                y = self.model(x_in)
                loss = criterion(y, x_in)

                # 勾配を初期化してBackProp
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                batch_loss += loss

                # vec_id 更新
                for idx, word_id in enumerate(pre_id):
                    self.word_info.words_dic_info[word_id]["vec_id"] = y[idx, 0].to("cpu").detach().numpy()

            bar.set_description("loss %.8f" % (batch_loss / len(self.data_set)))

        # save
        torch.save(self.model.state_dict(), self.out_path + "/elily.mdl")
        self.word_info.save(self.out_path + "/words_dat.pkl")


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i', '--input_path', help='input directory path', required=True)
    arg_parser.add_argument('-o', '--output_path', help='output model path', required=True)
    args = arg_parser.parse_args()

    trainer = Trainer(args.input_path, args.output_path)
    trainer(100, 2048)


if __name__ == "__main__":
    main()



