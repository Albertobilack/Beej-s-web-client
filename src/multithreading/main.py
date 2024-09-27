import threading, time, sys

def runner(name, count):
    for i in range(count):
        print(f"Running: {name}, iteration {i}")
        time.sleep(0.3)

THREAD_COUNT = 3

def main():

    threads = []

    for i in range(THREAD_COUNT):
        name = f"Thread{i}"

        t = threading.Thread(target = runner, args=(name, i+3))

        t.start()

        threads.append(t)

    for t in threads:
        t.join()


if __name__ == "__main__":
    sys.exit(main())