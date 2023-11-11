import multiprocessing
import time

def cube(x,vars):
    return (x+vars.y+vars.z)**3

class Vars:
    pass

if __name__ == "__main__":
    pool = multiprocessing.Pool(2)
    start_time = time.perf_counter()
    vars = Vars()
    vars.y = 10
    vars.z = 2
    processes = [pool.apply_async(cube, args=(x,vars)) for x in range(1,1000)]
    result = [pp.get() for pp in processes]
    finish_time = time.perf_counter()
    print(f"Program finished in {finish_time-start_time} seconds")
    #print(result)