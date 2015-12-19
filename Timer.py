import time

from threading import Thread, Timer

class CountDownTimer(Thread):
    def __init__(self, interval, target):
        Thread.__init__(self)
        self.target = target
        self.interval = interval
        self.daemon = True
        self.stopped = False

    def run(self):
        while not self.stopped:
            time.sleep(self.interval)
            self.target()

class ResetTimer(object):
    def __init__(self, interval, func_ptr, args=None):
        if args:
            assert type(args) is list
        self.func_ptr = func_ptr
        self.interval = interval
        self.args = args
        self.coundown_timer = self.new_timer()

    def new_timer(self):
        timer = Timer(self.interval, self.func_ptr, self.args)
        timer.daemon = True
        return timer

    def reset(self):
        self.stop()
        self.coundown_timer = self.new_timer()
        self.start()

    def start(self):
        self.coundown_timer.start()

    def stop(self):
        self.coundown_timer.cancel()