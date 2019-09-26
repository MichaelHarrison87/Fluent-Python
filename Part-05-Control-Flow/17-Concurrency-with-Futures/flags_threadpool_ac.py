# as flags_threadpool, but inspects each future directly

from concurrent import futures

from flags_sequential import save_flag, get_flag, show, main      # re-use these functions

MAX_WORKERS = 2

def download_one(cc):
    image = get_flag(cc)
    show(cc)
    save_flag(image, cc.lower() + '.gif')
    return cc

def download_many(cc_list):
    workers = min(MAX_WORKERS, len(cc_list))
    with futures.ThreadPoolExecutor(workers) as executor:
        to_do = []
        for cc in sorted(cc_list):
            future = executor.submit(download_one, cc)
            to_do.append(future)
            print(f'Scheduled for {cc}: {future}')
    
        results = []
        for future in futures.as_completed(to_do):
            res = future.result()
            print(f'{future} result: {res}')
            results.append(res)
        
    return len(results)


if __name__ == '__main__':
    main(download_many)