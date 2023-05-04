import multiprocessing
from argparse import ArgumentParser
from multiprocessing import Process
from neptunia.registry import registry

from neptunia.app import main, main_from_xml

if __name__ == '__main__':
    parser = ArgumentParser(description='Simple web crawler')
    parser.add_argument('-u', '--url', type=str, help='Url to visit')
    parser.add_argument('-w', '--wait', type=int, help='Waiting time')
    namespace = parser.parse_args()

    # registry.load()
    # registry.run_scrapper()
    process = Process(target=main, args=[False])

    try:
        process.start()
        process.join()
    except KeyboardInterrupt:
        process.close()
