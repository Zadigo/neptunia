import queue
import time
from multiprocessing import Pool, Process, Queue, current_process


def continent(continent='Asia'):
    print('The name of continent is:', continent)


def continent_from_queue(continents):
    # while True:
    try:
        continent = continents.get_nowait()
    except queue.Empty:
        pass
    else:
        current_process_name = current_process().name
        print('The name of continent is:', continent,
              'completed by process', current_process_name)
        time.sleep(2)


def continent_from_pool(data):
    process_name = current_process().name
    print('Continent is', data[0], process_name,
          'Waiting for', data[1], 'seconds')
    time.sleep(data[1])


if __name__ == "__main__":
    # 1. First method
    # process = Process(target=continent, kwargs={'continent': 'Google'})
    # process.start()
    # process.join()

    # 2. Second method with Queue
    # a = Queue()

    # for name in ['America', 'Africa']:
    #     a.put(name)

    # number_of_processes = 3
    # processes = []

    # for i in range(number_of_processes):
    #     process = Process(target=continent_from_queue, args=[a])
    #     processes.append(process)
    #     process.start()

    # for process in processes:
    #     process.join()

    # while not a.empty():
    #     a.get()

    # 3. Third method with Pool
    continents = (['Africa', 5], ['America', 2], ['Europe', 1], ['Asia', 3])
    pool = Pool(2)
    pool.map(continent_from_pool, continents)
