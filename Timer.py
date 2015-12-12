import time

from threading import Thread, Timer

class CountDownTimer(Thread):
    def __init__(self, timeout, target):
        Tread.__init__(self)
        self.daemon = True
        self.is_stopped = False
        self.target = target
        self.timeout = timeout

class ResetTimer(object):
    def __init__(self, timeout, func_ptr, args=None):
        if args:
            assert type(args) is list
        self.args = args
        self.func_ptr = func_ptr
        self.timeout = timeout
        self.coundown_timer = self.create_timer()

    def create_timer(self):
        timer = Timer(self.timeout, self.func_ptr, self.args)
        timer.daemon = True
        return timer

    def cancel(self):
        self.coundown_timer.cancel()