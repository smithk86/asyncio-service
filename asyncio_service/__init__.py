import atexit
import logging
import sys

from .service import AsyncioService


logger = logging.getLogger(__name__)
__VERSION__ = '1.2.4'
__DATE__ = '2021-01-19'
__MIN_PYTHON__ = (3, 7)
__all__ = ['AsyncioService']


if sys.version_info < __MIN_PYTHON__:
    sys.exit('python {}.{} or later is required'.format(*__MIN_PYTHON__))


@atexit.register
def shutdown_alert():
    if len(AsyncioService.running_services) > 0:
        list_of_names = ', '.join([svc.name for svc in AsyncioService.running_services])
        logger.warning(f'AsyncioService instances still running: {list_of_names}')
