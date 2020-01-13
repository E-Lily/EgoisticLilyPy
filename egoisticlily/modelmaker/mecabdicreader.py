# -*- coding: utf-8 -*-
"""
 Copyright (c) 2018-2019 Masahiko Hashimoto <hashimom@geeko.jp>

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
import argparse
import glob
from egoisticlily.modelmaker.wordholder import WordHolder


class MecabDicReader:
    def __init__(self, in_csv_dir, out_csv_dir):
        self.in_csv_dir = os.path.abspath(in_csv_dir)
        self.out_csv_dir = os.path.abspath(out_csv_dir + "/")

    def __call__(self):
        holder = WordHolder()
        csv_list = glob.glob(self.in_csv_dir + "/*.csv")
        for csv_file in csv_list:
            print(csv_file + " open")
            with open(csv_file, "r") as f:
                reader = csv.reader(f, delimiter=",")
                for row in reader:
                    holder.regist(row[0], row[9], row[4], row[5])

        holder.regist("@S@", "@S@", "PHASE", "SOP")
        holder.regist("@E@", "@E@", "PHASE", "EOP")
        holder.regist("@N@", "@N@", "PHASE", "NONE")
        holder.save(self.out_csv_dir)


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i', nargs='?', help='input csv directory', required=True)
    arg_parser.add_argument('-o', nargs='?', help='output directory', required=True)
    args = arg_parser.parse_args()

    reader = MecabDicReader(args.i, args.o)
    reader()


if __name__ == "__main__":
    main()


