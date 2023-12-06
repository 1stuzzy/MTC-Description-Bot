import threading

import psutil

cpu_usage = {}
cpu_usage['usage'] = psutil.cpu_percent()

exit_event = threading.Event()


def update_cpu_usage():
    while True:
        if exit_event.is_set():
            break
        cpu_usage['usage'] = psutil.cpu_percent(interval=1)
