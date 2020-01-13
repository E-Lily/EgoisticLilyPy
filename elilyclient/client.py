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
import grpc
import egoisticlily.proto.egoisticlily_pb2_grpc
import egoisticlily.proto.egoisticlily_pb2


def to_server(stub, kana):
    """ EgoisticLilyリクエスト送信

    :param stub:
    :param kana:
    :return:
    """
    response = stub.Convert(egoisticlily.proto.egoisticlily_pb2.ConvertReq(in_str=kana))
    print("漢字: " + response.out_str)


def main():
    """ EgoisticLily クライアントモジュール

    :return:
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-p', '--port', help='server port number', default='50055')
    args = arg_parser.parse_args()

    port_str = '[::]:' + args.port
    with grpc.insecure_channel(port_str) as channel:
        stub = egoisticlily.proto.egoisticlily_pb2_grpc.EgoisticLilyServiceStub(channel)
        print('--EgoisticLily Client--')
        while True:
            kana = input("かな > ")
            to_server(stub, kana)


if __name__ == '__main__':
    main()
