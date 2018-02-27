import os
import argparse
from re import compile
from shutil import copy2
import configparser

config = configparser.ConfigParser()
config.read('config.conf')

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
        self.rex_url = compile(r'http[s]?://([-\d\w.]+)')
        self.dst = self.path

    def copy_file(self, src, dst):
        if src:
            self.dst = self.path + self.rex_url.search(dst).group(1)
            if not os.path.exists(dst):
                os.mkdir(dst)
            copy2(src[0], self.dst)
        else:
            print('No files copy')

    def change_items_in_file(self, pattern):
        file = self.dst + 'index.php'
        print(self.path)
        with open(file) as r_file:
            tmp_file = self.rex_url.sub(pattern, r_file.read())
        with open(file, 'w') as w_file:
            w_file.write(tmp_file)


if __name__ == '__main__':
    argpars = argparse.ArgumentParser(prog='finger', usage='%(prog)s [options]', epilog='Finger parser half brain')
    argpars.add_argument('-u', '--url', help='Url target site')
    argpars.add_argument('-r', '--rex', default='', help='Regular expression pattern for search')
    argpars.add_argument('-p', '--path', default='.', help='Path work')

    args = vars(argpars.parse_args())

    finder = Finder(config.get('Main', 'path_files'))
    file_work = FileWorker(args.get('path'))
    files = finder.search(args.get('rex'), config.get('Main', 'search_files'), sort=True)
    file_work.copy_file(files, args.get('url'))
    file_work.change_items_in_file(args.get('url'))
