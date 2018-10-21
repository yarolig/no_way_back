from __future__ import print_function
from . import data

def main():
    print("Hello from your game's main()")
    print(data.load('sample.txt').read())
