import multiprocessing
from argparse import ArgumentParser
from multiprocessing import Process

from neptunia.neptunia.app import main

if __name__ == '__main__':
    parser = ArgumentParser(description='Simple web crawler')
    parser.add_argument('-u', '--url', type=str)
    namespace = parser.parse_args()

    process = Process(target=main, args=[False])
    process.start()
    process.join()
