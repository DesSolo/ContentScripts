import os
from sys import argv
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


finder = Finder('/home/dmitry/repo/parsers/src-parsers/www')
file_work = FileWorker('./')
files = finder.search(argv[1], 'index.php', sort=True)
file_work.copy_file(files[0], argv[2])
