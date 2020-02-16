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
import torch.nn as nn
import torch.nn.functional as F


class ELilyModel(nn.Module):
    def __init__(self, hid_dim=128, z_dim=32, hid_num=2, pos_id_num=43):
        """ コスト算出AEモデル

        :param hid_dim:
        :param z_dim:
        :param hid_num:
        :param pos_id_num:
        :param pos_id_num:
        """
        super(ELilyModel, self).__init__()
        self.hid_num = hid_num

        # Input Layer
        in_dim = (1 + pos_id_num) * 2
        self.in_layer = nn.Linear(in_dim, hid_dim)

        # encoder
        en_hid_layer = [nn.Linear(hid_dim, hid_dim) for _ in range(hid_num)]
        self.en_hid_layer = nn.ModuleList(en_hid_layer)
        self.en_z_layer = nn.Linear(hid_dim, z_dim)

        # decoder
        self.de_z_layer = nn.Linear(z_dim, hid_dim)
        de_hid_layer = [nn.Linear(hid_dim, hid_dim) for _ in range(hid_num)]
        self.de_hid_layer = nn.ModuleList(de_hid_layer)

        # Output Layer
        self.out_layer = nn.Linear(hid_dim, in_dim)

    def forward(self, x_in):
        """ 順伝搬

        :param x_in:
        :return:
        """
        # encoder
        x = F.relu(self.in_layer(x_in))
        for i in range(self.hid_num):
            x = self.en_hid_layer[i](x)
        z = F.relu(self.en_z_layer(x))

        # decoder
        x = F.relu(self.de_z_layer(z))
        for i in range(self.hid_num):
            x = self.en_hid_layer[i](x)
        y = self.out_layer(x)
        return y
