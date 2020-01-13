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
import numpy as np


class Words:
    def __init__(self):
        self.word_type_list = [
            [
                "形容詞",
                "連体詞",
                "副詞",
                "判定詞",
                "助動詞",
                "接続詞",
                "指示詞",
                "感動詞",
                "名詞",
                "動詞",
                "助詞",
                "接頭辞",
                "接尾辞",
                "特殊",
                "未定義語",
                "PHASE"
            ],
            [
                "形容詞",
                "連体詞",
                "副詞",
                "判定詞",
                "助動詞",
                "接続詞",
                "名詞形態指示詞",
                "連体詞形態指示詞",
                "副詞形態指示詞",
                "感動詞",
                "普通名詞",
                "副詞的名詞",
                "形式名詞",
                "固有名詞",
                "組織名",
                "地名",
                "人名",
                "サ変名詞",
                "数詞",
                "時相名詞",
                "動詞",
                "格助詞",
                "副助詞",
                "接続助詞",
                "終助詞",
                "名詞接頭辞",
                "動詞接頭辞",
                "イ形容詞接頭辞",
                "ナ形容詞接頭辞",
                "名詞性名詞接尾辞",
                "名詞性述語接尾辞",
                "名詞性名詞助数辞",
                "名詞性特殊接尾辞",
                "形容詞性述語接尾辞",
                "形容詞性名詞接尾辞",
                "動詞性接尾辞",
                "句点",
                "読点",
                "括弧始",
                "括弧終",
                "記号",
                "空白",
                "カタカナ",
                "アルファベット",
                "その他",
                "SOP",
                "EOP",
                "NONE"
            ]
        ]

        self.type1_one_hot = np.eye(len(self.word_type_list[0]), dtype="float32")
        self.type2_one_hot = np.eye(len(self.word_type_list[1]), dtype="float32")
        self.vec_id_bit_num = 16

    def __call__(self, vec_id, type1, type2):
        id_ary = []
        tmp = vec_id
        for i in range(self.vec_id_bit_num):
            if tmp & 1:
                id_ary.append(1.)
            else:
                id_ary.append(0.)
            tmp = tmp >> 1

        ret_ary = np.array(id_ary, dtype="float32")
        ret_ary = np.hstack((ret_ary, self.type1_one_hot[int(type1)]))
        ret_ary = np.hstack((ret_ary, self.type2_one_hot[int(type2)]))
        return ret_ary
