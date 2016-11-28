import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

special_words = {' And ': ' and ', ' Or ': ' or ',
                   ' Of ': ' of ', ' Da ': ' da '
                   , ' La ': ' la ', ' De ': ' de ',
                   '\'S': '\'s', 'D\'': 'd\''}

def process_line(line):
    name = line.split('"')[3]
    name1 = name.title()
    for key, val in special_words.viewitems():
        name1 = name1.replace(key, val)
    return line.replace(name, name1)


if __name__ == '__main__':
    file_name = sys.argv[1]
    new_file = '{}.txt'.format(file_name)
    new_ff = open(new_file, 'w+')
    ff = open(file_name, 'r')
    for line in ff:
        if line.find('"name"') >= 0:
            line = process_line(line)
        new_ff.write(line)
    new_ff.close()
    ff.close()
