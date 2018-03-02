import os
from re import compile
from shutil import copy2
import configparser
from subprocess import Popen, PIPE
from pyquery import PyQuery as pq

config = configparser.ConfigParser()
config.read('config.conf')


class Parser(object):
    def __init__(self, pattern):
        self.pattern = ','.join(['a:contains("{}")'.format(item) for item in pattern.split(';')])
        self.regexp = None

    def parse(self, url):
        class_list = []
        try:
            soup = pq(url=url)
            for elem in soup(self.pattern):
                class_list += (str(pq(elem).attr('class')).split())
                class_list += (str(pq(elem).parent().attr('class')).split())
                class_list += (str(pq(elem).parent().parent().attr('class')).split())
            self.regexp = '|'.join(set(class_list))
        except Exception as ex:
            print(ex, 'Parse error!', sep='\n')


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
            print('No files to copy')

    def change_items_in_file(self, pattern):
        file = self.dst + '/' + 'index.php'
        if os.path.isfile(file):
            with open(file) as r_file:
                tmp_file = self.rex_url.sub(self.rex_url.search(pattern).group(0), r_file.read())
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


