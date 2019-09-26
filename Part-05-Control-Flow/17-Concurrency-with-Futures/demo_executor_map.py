import time
from datetime import datetime
from concurrent import futures


def display(*args):
    
    print('[' + datetime.now().strftime("%H:%M:%S.%f")[:-3] + ']', end = ' ')
    print(*args)
    
def loiter(n):
    msg = '{}loiter({}): doing nothing for {}s...'
    display(msg.format('\t'*n, n, n))
    time.sleep(n)
    msg = '{}loiter({}): done'
    display(msg.format('\t'*n, n))
    return  n * 10

def main():
    t0 = time.time()
    display('Script starting')
    executor = futures.ThreadPoolExecutor(max_workers=10)
    results = executor.map(loiter, range(1, 11))
    display('results:', results)
    display('Waiting for individual results')
    for i, result in enumerate(results):
        display(f'result {i}: {result}')
    print('ELAPSED:', time.time() - t0)
if __name__ == '__main__':
    main()