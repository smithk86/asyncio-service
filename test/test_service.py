# add the project directory to the pythonpath
import os.path
import sys
from pathlib import Path
dir_ = Path(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, str(dir_.parent))


import asyncio

import pytest

from asyncio_service import AsyncioService
from timer import Timer


class _TestAsyncioService(AsyncioService):
    def __init__(self, *, name=None):
        super().__init__(name=name)
        self.cleanup_has_been_called = False
        self.results = list()

    async def run(self):
        numbers = iter(range(99))
        while self.running():
            self.results.append(next(numbers))
            await asyncio.sleep(.25)

    async def cleanup(self):
        self.cleanup_has_been_called = True


class _TestAsyncioServiceWithException(AsyncioService):
    def __init__(self, *, name=None):
        super().__init__(name=name)

    async def run(self):
        raise RuntimeError('forced-exception')


class _TestAsyncioServiceWaitForRunning(AsyncioService):
    def __init__(self, *, name=None):
        super().__init__(name=name)

    async def run_wrapper(self):
        await asyncio.sleep(.5)
        await super().run_wrapper()

    async def run(self):
        await asyncio.sleep(.5)


@pytest.mark.asyncio
async def test_base():
    # init
    service = _TestAsyncioService()
    assert service.name == '_TestAsyncioService'
    # assert service._task = None
    assert service._task is None
    assert service.cleanup_has_been_called is False
    assert service.running() is None

    # start and allow to run
    task = service.start()
    assert type(service._task) is asyncio.Task
    assert task is service._task
    await asyncio.sleep(3)

    # verify it is running
    assert service.running() is True
    assert task.done() is False

    # stop and verify
    await service.stop()
    assert service.running() is False
    assert service._task.done() is True

    assert service.cleanup_has_been_called is True
    assert len(service.results) == 12
    assert service.results == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


@pytest.mark.asyncio
async def test_service():
    service = _TestAsyncioService(name='pytest_service')
    assert service.name == 'pytest_service'


@pytest.mark.asyncio
async def test_exception():
    async with _TestAsyncioServiceWithException(name='pytest_service_with_exception') as service:
        pass
    assert service.name == 'pytest_service_with_exception'
    assert type(service.exception) is RuntimeError


@pytest.mark.asyncio
async def test_wait_for_running():
    with Timer(name='service') as t1:
        async with _TestAsyncioServiceWaitForRunning(name='pytest_service_wait_for_running') as service:
            with Timer(name='wait_for_running') as t2:
                await service.wait_for_running()
            assert t2.seconds >= .5
    assert t1.seconds >= 1
    assert service.name == 'pytest_service_wait_for_running'

    # confirm start() throws RuntimeError is tried to be restarted
    with pytest.raises(RuntimeError) as exc:
        service.start()
    assert str(exc.value) == 'task has already been started'


@pytest.mark.asyncio
async def test_stop_all():
    assert type(AsyncioService.running_services) is list
    assert len(AsyncioService.running_services) == 0

    tasks = list()
    # init
    for i in range(5):
        s = _TestAsyncioService(name=f'_TestAsyncioService{i}')
        tasks.append(s.start())

    await asyncio.sleep(1)

    assert len(AsyncioService.running_services) == 5
    await AsyncioService.stop_all()
    assert len(AsyncioService.running_services) == 0
