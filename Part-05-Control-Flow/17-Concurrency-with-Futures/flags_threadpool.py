from concurrent import futures

from flags_sequential import save_flag, get_flag, show, main      # re-use these functions

MAX_WORKERS = 20

def download_one(cc):
    image = get_flag(cc)
    show(cc)
    save_flag(image, cc.lower() + '.gif')
    return cc

def download_many(cc_list):
    workers = min(MAX_WORKERS, len(cc_list))
    with futures.ThreadPoolExecutor(workers) as executor:
        res = executor.map(download_one, sorted(cc_list))
    
    return len(list(res))


if __name__ == '__main__':
    main(download_many)