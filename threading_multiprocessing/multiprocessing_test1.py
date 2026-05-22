"""
Multiprocessing & the GIL


First: What is the GIL?
The Global Interpreter Lock is a mutex inside CPython that allows only one thread to execute Python bytecode at a time — even on a multi-core machine.
Thread 1: ──█████░░░░░░░██████░░░░░░░░█████──
Thread 2: ──░░░░░██████░░░░░░░██████░░░░░░░──
                ↑ only one runs at a time
This means threading does NOT give you true parallelism for CPU-bound tasks.

Why the GIL exists
CPython manages memory with reference counting. Every object tracks how many references point to it. Without the GIL, two threads could modify a refcount simultaneously → corruption → crash. The GIL is the simple (if blunt) solution.
python# This is NOT thread-safe without the GIL:
x.refcount += 1   # thread 1
x.refcount += 1   # thread 2  ← could read stale value

The Solution: multiprocessing
multiprocessing spawns separate OS processes, each with its own Python interpreter and its own GIL. They run truly in parallel on multiple cores.
Process 1: [Python interpreter + GIL] ──█████████──  Core 0
Process 2: [Python interpreter + GIL] ──█████████──  Core 1
Process 3: [Python interpreter + GIL] ──█████████──  Core 2
Process 4: [Python interpreter + GIL] ──█████████──  Core 3
The tradeoff: processes don't share memory, so communication has overhead.
"""
from multiprocessing import Process

def worker(name):
    print(f"Process {name} running")

if __name__ == "__main__":       # ← required on Windows/macOS
    processes = [Process(target=worker, args=(i,)) for i in range(4)]

    for p in processes:
        p.start()

    for p in processes:
        p.join()                 # wait for all to finish

    print("All done")
