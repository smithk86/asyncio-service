import asyncio
import logging
import sys
from abc import abstractmethod


logger = logging.getLogger(__name__)
__VERSION__ = '1.2.0'
__DATE__ = '2020-09-09'
__MIN_PYTHON__ = (3, 7)


if sys.version_info < __MIN_PYTHON__:
    sys.exit('python {}.{} or later is required'.format(*__MIN_PYTHON__))


class AsyncioService(object):
    def __init__(self, *, name=None, **kwargs):
        super().__init__()
        if name:
            self.name = name
        else:
            self.name = self.__class__.__name__
        self._running = None
        self._task = None
        self.exception = None

    async def __aenter__(self):
        self.start()
        return self

    async def __aexit__(self, *exc):
        await self.stop()

    def start(self):
        loop = asyncio.get_running_loop()
        logger.info(f'starting service: {self.name}')
        self._task = loop.create_task(self.run_wrapper())
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
            await self.close()
            logger.debug(f'service has stopped: {self.name}')

    @abstractmethod
    async def run(self):
        pass

    def running(self):
        return self._running

    async def close(self):
        pass
