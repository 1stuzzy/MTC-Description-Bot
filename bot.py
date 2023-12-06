import threading

from aiogram import Dispatcher, executor
from loguru import logger

from Package.models import connect, disconnect
from loader import config, dp, status_names
from utils.notify import on_startup_notify
from utils.logger_config import setup_logger
from utils.systeminfo import update_cpu_usage, exit_event
from utils.basefunctional import set_status
from utils.updaterepo import check_on_update


async def on_startup(dispatcher: Dispatcher):
    connect()

    for admin_id in config.admins_id:
        set_status(admin_id, len(status_names.VALUES) - 1)

    setup_logger(level="DEBUG")

    from utils import filters, middlewares

    filters.setup(dispatcher)
    middlewares.setup(dispatcher)

    logger.info("Setuping handlers...")
    import handlers

    #check_on_update()
    if config.notify:
        await on_startup_notify(dispatcher)


async def on_shutdown(_):
    disconnect()
    exit_event.set()


def main():
    c_usage = threading.Thread(target=update_cpu_usage)
    c_usage.name = "CpuUsageUpdater"
    c_usage.start()

    executor.start_polling(
        dp,
        skip_updates=config.skip_updates,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        timeout=5,
    )


if __name__ == "__main__":
    main()
