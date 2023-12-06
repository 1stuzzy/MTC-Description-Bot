from typing import Tuple, List, Union

from aiogram import Bot
from aiogram.utils.exceptions import (
    CantParseEntities,
    ChatNotFound,
    BotBlocked,
    UserDeactivated,
    NetworkError,
)
from loguru import logger


async def alert_users(
    text: str, users: Union[Tuple[Union[int, str]], List[Union[int, str]]], bot: Bot
):
    if not isinstance(bot, Bot):
        raise TypeError(
            f"Argument 'bot' must be an instance of Bot, not '{type(bot).__name__}'"
        )

    answer = {
        "msg_count": 0,
        "block_count": 0,
        "notfound_count": 0,
        "deactivated_count": 0,
        "network_count": 0,
        "cantparse_count": 0,
        "internal_count": 0,
    }

    for user_id in users:
        try:
            await bot.send_message(user_id, text)
            answer["msg_count"] += 1
            logger.debug(f"Alert message has been successfully sent to user {user_id}")
            # await sleep(0.2)
        except CantParseEntities as ex:
            answer["cantparse_count"] += 1
            logger.error(
                "Notification failed. aiogram couldn't properly parse the following text:\n"
                f"Exception: {ex}",
            )
        except ChatNotFound:
            answer["notfound_count"] += 1
            logger.error(
                f"Notification failed. User {user_id} hasn't started the bot yet"
            )
        except BotBlocked:
            answer["block_count"] += 1
            logger.error(f"Notification failed. User {user_id} has blocked the bot")
        except UserDeactivated:
            answer["deactivated_count"] += 1
            logger.error(
                f"Notification failed. User {user_id}'s account has been deactivated"
            )
        except NetworkError:
            answer["network_count"] += 1
            logger.critical(
                "Could not access https://api.telegram.org/. Check your internet connection"
            )
        except Exception as ex:
            answer["internal_count"] += 1
            logger.exception(ex)
        yield answer
