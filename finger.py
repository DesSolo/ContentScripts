import finger as lib
import argparse

config = lib.config

if __name__ == '__main__':
    argpars = argparse.ArgumentParser(prog='finger', usage='%(prog)s [options]', epilog='Finger parser half brain')
    argpars.add_argument('-u', '--url', help='Url target site')
    argpars.add_argument('-r', '--rex', default='', help='Regular expression pattern for search')
    argpars.add_argument('-p', '--path', default='parsers', help='Path work')

    args = vars(argpars.parse_args())

    finder = lib.Finder(config.get('Main', 'path_files'))
    runner_php = lib.StarterPHP()
    file_work = lib.FileWorker(args.get('path'))
    regexp = args.get('rex')
    if not regexp:
        parser = lib.Parser(config.get('Parser', 'items'))
        parser.parse(args.get('url'))
        regexp = parser.regexp

    files = finder.search(regexp, config.get('Main', 'search_files'), sort=True)
    len_files = len(files)
    iterator = len(files) + 1
    print('Fond files: {}'.format(len_files))
    for file in files:
        file_work.copy_file(file, args.get('url'))
        current_file = file_work.change_items_in_file(args.get('url'))
        if current_file:
            if runner_php.run(current_file):
                print('Finished Success!')
                break
            else:
                len_files -= 1
                print('[{}]/[{}] No profit...'.format(iterator, len_files))