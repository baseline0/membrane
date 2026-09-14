#!/usr/bin/python3


import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)


from cyprus.program import parse_and_run_tree

# -------------------

if __name__ == "__main__":
    fname = "./tests/examples/example1.cyp"
    # fname = "./tests/examples/hello.cyp"
    parse_and_run_tree(fname, pverbose=True)
