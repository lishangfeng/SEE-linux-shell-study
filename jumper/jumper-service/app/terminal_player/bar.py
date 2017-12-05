# -*- coding:utf-8 -*-


class Bar:
    def __init__(self, total=0, count=0, width=100):
        self.count = count
        self.total = total
        self.width = width
        self.play = True

    def move(self, step=1):
        self.count += step

    def get_bar(self, text):
        data = list()
        progress = self.width * self.count / self.total

        data.append(' ' * (self.width + 100) + '\r')
        data.append(text)
        data.append(self.get_icon())
        data.append('#' * progress + '-' * (self.width - progress))
        data.append(self.get_time())
        if progress == self.width:
            data.append('\n')
        return data

    def get_icon(self):
        if self.play:
            return u'➤ | '
        else:
            return u'▇ | '

    def get_time(self):
        return u' | {0:3}/{1:3}\r'.format(self.count, self.total)
