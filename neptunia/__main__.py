import multiprocessing
from argparse import ArgumentParser
from multiprocessing import Process
# from neptunia.neptunia.registry import registry

from neptunia.app import main

if __name__ == '__main__':
    parser = ArgumentParser(description='Simple web crawler')
    parser.add_argument('-u', '--url', type=str, help='Url to visit')
    parser.add_argument('-w', '--wait', type=int, help='Waiting time')
    namespace = parser.parse_args()

    # registry.load_registry()
    process = Process(target=main, args=[False])

    try:
        process.start()
        process.join()
    except KeyboardInterrupt:
        process.close()
