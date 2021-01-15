from datetime import datetime


class Timer(object):
    def __init__(self, name=None):
        self.name = name
        self.start = datetime.now()
        self.end = None

    def __repr__(self):
        seconds = self.seconds() if self.end else ''
        name = self.name if self.name else ''
        return f'<object Timer name={name} seconds={seconds}>'

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.stop()

    def stop(self):
        self.end = datetime.now()

    @property
    def timedelta(self):
        return self.end - self.start

    @property
    def seconds(self):
        return self.timedelta.total_seconds()

    @property
    def microseconds(self):
        return self.timedelta.microseconds

    @property
    def milliseconds(self):
        return int(self.microseconds / 1000)
