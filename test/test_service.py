# add the project directory to the pythonpath
import os.path
import sys
from pathlib import Path
dir_ = Path(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, str(dir_.parent))


import asyncio

import pytest

from asyncio_service import AsyncioService


class _TestAsyncioService(AsyncioService):
    def __init__(self):
        super().__init__()
        self.close_has_been_called = False
        self.results = list()

    async def run(self):
        numbers = iter(range(99))
        while self.running():
            self.results.append(next(numbers))
            await asyncio.sleep(.25)

    async def close(self):
        self.close_has_been_called = True


@pytest.mark.asyncio
async def test_service():
    service = _TestAsyncioService()
    assert service.name == 'asyncio_service'
    assert service.running() is None

    task = service.start()
    await asyncio.sleep(3)

    # verify it is running
    assert service.running() is True
    assert task.done() is False

    # stop and verify
    await service.stop()
    assert service.running() is False
    assert task.done() is True

    assert len(service.results) == 12
    assert service.results == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
