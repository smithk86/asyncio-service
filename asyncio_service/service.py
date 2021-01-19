import asyncio
import logging
from abc import abstractmethod


logger = logging.getLogger(__name__)


class classproperty(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


class AsyncioService(object):
    _running_services = list()

    def __init__(self, *, name=None, **kwargs):
        super().__init__()
        if name:
            self.name = name
        else:
            self.name = self.__class__.__name__
        self._running = None
        self._task = None
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
        AsyncioService._running_services.append(self)
        logger.info(f'starting service: {self.name}')
        self._task = self.loop.create_task(self.run_wrapper())
        return self._task

    async def stop(self):
        if self._task:
            logger.warning(f'stopping service: {self.name}')
            self._running = False
            await self._task
            self._task = None

    async def run_wrapper(self):
        self._running = True
        try:
            await self.run()
        except Exception as e:
            logger.exception(e)
            self.exception = e
        finally:
            self._running = False
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
        return self._running

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