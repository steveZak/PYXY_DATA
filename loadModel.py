import gensim
import os
import shutil
import hashlib
from sys import platform

def getFileLineNums(filename):
    f = open(filename, 'r')
    count = 0
    for line in f:
        count += 1
    return count


def prepend_line(infile, outfile, line):
    with open(infile, 'r') as old:
        with open(outfile, 'w') as new:
            new.write(str(line) + "\n")
            shutil.copyfileobj(old, new)

def prepend_slow(infile, outfile, line):
    with open(infile, 'r') as fin:
        with open(outfile, 'w') as fout:
            fout.write(line + "\n")
            for line in fin:
                fout.write(line)

def load(filename):
    # num_lines = getFileLineNums(filename)
    # gensim_file = 'glove_model.txt'
    # gensim_first_line = "{} {}".format(num_lines, 300)
    # # Prepends the line.
    # if platform == "linux" or platform == "linux2":
    #     prepend_line(filename, gensim_file, gensim_first_line)
    # else:
    #     prepend_slow(filename, gensim_file, gensim_first_line)
    # print("prepended the line")
    model = gensim.models.KeyedVectors.load_word2vec_format(os.getcwd()+'/glove_model.txt')
    print("loaded the model")
    return model