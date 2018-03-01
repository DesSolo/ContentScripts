from pyquery import PyQuery as pq


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