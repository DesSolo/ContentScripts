import os
from sys import argv
import argparse
from re import compile
from shutil import copy2


class Finder(object):
    def __init__(self, path):
        self.path = path

    def get_all_files(self):
        for path, _, files in os.walk(self.path):
            for name in files:
                yield os.path.join(path, name)

    def get_only(self, name):
        for item in self.get_all_files():
            if name in item:
                yield item

    def search(self, pattern, names, sort=True):
        result = []
        pattern = compile(pattern)
        for item in self.get_only(names):
            try:
                with open(item, 'r') as file:
                    if pattern.search(file.read()):
                        result.append(item)
            except Exception as ex:
                print(ex)
        if sort:
            crtime = {}
            for file in result:
                crtime[(os.path.getmtime(file))] = file
            result = []
            for time in sorted(crtime, reverse=True):
                result.append(crtime[time])
        return result


class FileWorker(object):
    def __init__(self, path):
        self.path = path if path[-1] == '/' else path + '/'

    def copy_file(self, src, dst):
        dst = self.path + dst
        if not os.path.exists(dst):
            os.mkdir(dst)
        copy2(src, dst)

    def change_items_in_file(self, pattern, file):
        file = self.path + file + 'index.php'
        rex_url = compile(r'http[s]?://[\d\w.]+')
        with open(file) as r_file:
            tmp_file = rex_url.sub(pattern, r_file.read())
        with open(file, 'w') as w_file:
            w_file.write(tmp_file)

# argpars = argparse.ArgumentParser(prog='finger', usage='%(prog)s [options]', epilog='Finger parser half brain')
# argpars.add_argument('-u', '--url', help='Url audiobook')
# argpars.add_argument('-p', '--path', default='' ,help='Path to download')
# argpars.add_argument('-t', '--threads', type=int, default=7, help='How many threads for downloading')

finder = Finder('/home/dmitry/repo/parsers/src-parsers/www')
file_work = FileWorker('./')
files = finder.search(argv[1], 'index.php', sort=True)
file_work.copy_file(files[0], argv[2])
file_work.change_items_in_file(argv[3], argv[2])