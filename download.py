#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import getopt
import sys
import os
import re

from sys import argv
from PIL import Image


def make_dir(path):
    path = path.strip()
    path = path.rstrip("\\")
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def save_file(path, file_name, data):
    if data is None:
        return
    make_dir(path)
    if not path.endswith("/"):
        path = path + "/"
    open_file = open(path + file_name, "wb")
    open_file.write(data)
    open_file.flush()
    open_file.close()


def show_help():
    print("Usage: %s [options] url" % argv[0])
    show_version()
    print("--input   		-i	Picture download url")
    print("--output  		-o	Download file save address")
    print("--all-size		-a	Download all size of picture")
    print("--format 		-f	Picture format (default jpg)")
    print("--help   		-h	Help information")
    print("--version		-v	Version information")


def show_version():
    print("Dmp download version 1.0.0 EternalZZX")


def download_pic(pic_url, download_path='download', only_max=True, pic_format='jpg'):
    pic_url = re.split('path=', pic_url)[1].replace('.xml', '') + '_files/'
    folder = 13 if only_max else 0
    x, y = 0, 0
    x_max, y_max = 0, 0
    while folder <= 13:
        while True:
            download_url = 'http://en.dpm.org.cn' + pic_url + str(folder) + \
                           '/' + str(x) + '_' + str(y) + '.' + pic_format
            result = requests.get(download_url)
            print('Response: ' + str(result.status_code) + ' ' + download_url)
            if result.status_code == 200:
                file_name = str(x) + '_' + str(y) + '.' + pic_format
                save_file(download_path + '/' + str(folder) + '/', file_name,
                          result.content)
                y_max = max(y, y_max)
                y = y + 1
            else:
                if y == 0:
                    x = 0
                    break
                else:
                    x_max = max(x, x_max)
                    x = x + 1
                    y = 0
        folder = folder + 1
    print('Download Finish!')
    return x_max, y_max


def merge_pic(x_max, y_max, download_path='download', only_max=True, pic_format='jpg'):
    folder = 13 if only_max else 0
    while folder <= 13:
        image_first = Image.open(download_path + '/' + str(folder) + '/0_0.jpg')
        image_last_x = Image.open(download_path + '/' + str(folder) + '/' + str(x_max) + '_0.' + pic_format)
        image_last_y = Image.open(download_path + '/' + str(folder) + '/0_' + str(y_max) + '.' + pic_format)
        (block_width, block_height) = image_first.size
        (last_width, _) = image_last_x.size
        (_, last_height) = image_last_y.size
        result_width = block_width * x_max + last_width
        result_height = block_height * y_max + last_height
        image_result = Image.new('RGB', (result_width, result_height))
        pic_path = download_path + '/' + str(folder) + '/'
        for x in range(0, x_max + 1):
            for y in range(0, y_max + 1):
                image_block = Image.open(pic_path + str(x) + '_' + str(y) + '.' + pic_format)
                image_result.paste(image_block, (x * block_width, y * block_height))
        image_result.save(download_path + '/pic_' + str(folder) + '.jpg')
        folder = folder + 1
    print('Save Finish!')


if "__main__" == __name__:
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "hi:o:af:v",
                                   ["help", "input=", "output=",
                                    "all-size", "format=", "version"])
    except getopt.GetoptError as e:
        print('Error: ' + str(e))
        show_help()
        sys.exit(2)

    url = ''
    save_path = 'download'
    is_only_max = True
    img_format = 'jpg'
    for o, a in opts:
        if o in ("-v", "--version"):
            show_version()
        elif o in ("-h", "--help"):
            show_help()
            sys.exit()
        elif o in ("-i", "--input"):
            url = a
        elif o in ("-o", "--output"):
            save_path = a
        elif o in ("-a", "--all-size"):
            is_only_max = False
        elif o in ("-f", "--format"):
            img_format = a
        else:
            show_help()
            assert False, "Unhandled option"
    if not url:
        try:
            url = args[0]
        except IndexError:
            show_help()
            sys.exit(2)
    try:
        index_x, index_y = download_pic(url, download_path=save_path,
                                        only_max=is_only_max,
                                        pic_format=img_format)
        merge_pic(index_x, index_y,
                  download_path=save_path,
                  only_max=is_only_max,
                  pic_format=img_format)
    except Exception as e:
        print('Error: ' + str(e))
        sys.exit(1)
