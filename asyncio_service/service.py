import asyncio
import logging
from abc import abstractmethod
from datetime import datetime

from pytz import utc


logger = logging.getLogger(__name__)


def now():
    return utc.localize(datetime.utcnow())


class classproperty(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


class AsyncioService(object):
    _running_services = list()
    _index = 0

    def __init__(self, *, name=None, **kwargs):
        super().__init__()
        if name:
            self.name = name
        else:
            self.name = self.__class__.__name__
        self._task = None
        self.start_date = None
        self.end_date = None
        self.exception = None

    @property
    def loop(self):
        return asyncio.get_running_loop()

    def __repr__(self):
        return f'<asyncio_service.AsyncioService object: {self.name}>'

    async def __aenter__(self):
        self.start()
        return self

    async def __aexit__(self, *exc):
        await self.stop()

    def start(self):
        if self._task is not None:
            raise RuntimeError('task has already been started')

        AsyncioService._running_services.append(self)
        logger.info(f'starting service: {self.name}')
        index = AsyncioService.get_next_index()
        self._task = self.loop.create_task(self.run_wrapper(), name=f'AsyncioServiceTask-{index}')
        return self._task

    async def stop(self):
        if self._task:
            logger.warning(f'stopping service: {self.name}')
            self.end_date = now()
            await self._task

    async def run_wrapper(self):
        self.start_date = now()
        try:
            await self.run()
        except Exception as e:
            logger.exception(e)
            self.exception = e
        finally:
            self.end_date = now()
            logger.debug(f'closing service: {self.name}')
            await self.cleanup()
            logger.debug(f'service has stopped: {self.name}')

            if self in AsyncioService._running_services:
                AsyncioService._running_services.remove(self)
            else:
                logger.warning('this service was not found in AsyncioService._running_services [name={self.name}]')

    @abstractmethod
    async def run(self):
        pass

    def running(self):
        if self.start_date is None:
            return None
        else:
            if self.end_date is None:
                return True
            else:
                return False

    async def wait_for_running(self, interval=0.05):
        while self.running() is not True:
            await asyncio.sleep(interval)

    async def cleanup(self):
        pass

    @classproperty
    def running_services(cls):
        return list(cls._running_services)

    @classmethod
    async def stop_all(cls):
        futures = list()
        for svc in cls.running_services:
            futures.append(svc.stop())
        await asyncio.wait(futures)
        assert len(cls.running_services) == 0

    @classmethod
    def get_next_index(cls):
        try:
            return cls._index
        finally:
            cls._index += 1
