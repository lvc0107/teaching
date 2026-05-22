import threading
import multiprocessing
import time

def cpu_task(n):
    """Pure CPU work — counts down from n"""
    while n > 0:
        n -= 1

N = 50_000_000

def run_threading():
    # --- Threading (GIL blocks true parallelism) ---
    start = time.time()
    threads = [threading.Thread(target=cpu_task, args=(N,)) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"Threading:      {time.time() - start:.2f}s")  # ~8s (slower than serial!)

def run_multiprocessing():
    # --- Multiprocessing (true parallelism) ---
    start = time.time()
    procs = [multiprocessing.Process(target=cpu_task, args=(N,)) for _ in range(4)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    print(f"Multiprocessing: {time.time() - start:.2f}s")  # ~2s (4x faster)

def main():
    run_threading()
    run_multiprocessing()

if __name__ == '__main__':
    # Safe on all platforms; required when using spawn on Windows/macOS
    multiprocessing.freeze_support()
    main()
