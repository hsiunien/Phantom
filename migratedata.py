#! /usr/bin/env python
import os
import re

DATA_STRUCT_PREFIX = "CREATE TABLE "
IGNORE_LINE_PREFIX = ["CONSTRAINT", "PRIMARY", "INSERT", "FOREIGN", "UNIQUE", "CHECK","CREATE"]


class Table:
    def __init__(self, table_name):
        self.table_name = table_name
        self.attributes = []
        self.recorders = []

    def print_data(self):
        print('%s,%s' % (self.table_name, self.attributes))

    def get_columns(self):
        return '`' + '`,`'.join(self.attributes) + '`'


def main():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    f2 = open(os.path.join(base_dir, "tbl_change.sql"), 'w')
    with open(os.path.join(base_dir, "prod.sql")) as sql_file:
        state = 0
        tbl = None
        for line in sql_file:
            rs = re.match(r'CREATE TABLE.*?(\w+?)\W+\(', line)
            if rs:
                if tbl:
                    tbl.print_data()
                tbl = Table(rs.group(1))
                state = 1
                # continue
            if state == 1:  # 处理create中的数据
                rs = re.match(r'.*?(\w+).*', line)
                if rs and is_not_column(rs.group(1)):
                    for eline in line.split(","):
                        e_first_words = re.match(r'.*?(\w+).*', eline)
                        if e_first_words and is_not_column(e_first_words.group(1)):
                            tbl.attributes.append(e_first_words.group(1))
                elif rs:
                    pass
                    # continue
                else:
                    state = 2
                    # continue
            if state == 2:
                rx = re.match('^INSERT INTO "' + tbl.table_name + '" VALUES.*', line)
                if rx:
                    print(line)
                    replacestr = 'INSERT INTO `' + tbl.table_name + '`(' + tbl.get_columns() + ') VALUES'
                    line = re.sub('^INSERT INTO "' + tbl.table_name + '" VALUES', replacestr, line)
                    pass
                else:
                    # tbl.print_data()
                    pass
            f2.write(line)
        f2.close()


def is_not_column(line_first):
    return line_first not in IGNORE_LINE_PREFIX


if __name__ == '__main__':
    main()
    # print(re.match(r'CREATE TABLE.*?(\w+?)\W+\(', r'''CREATE TABLE follow (''').group(1))
    # url = 'http://113.215.20.136:9011/113.215.6.77/c3pr90ntcya0/youku/6981496DC9913B8321BFE4A4E73/0300010E0C51F10D86F80703BAF2B1ADC67C80-E0F6-4FF8-B570-7DC5603F9F40.flv'
    # pattern = 'http://(.*?):9011/'
    # out = re.sub(pattern, 'http://127.0.0.1:9091/', url)
    # print(out)
