from aiogram import Dispatcher

from .whois import (
    Access_Filter,
    IsAdminFilter,
    IsUserFilter
)


def setup(dp: Dispatcher):
    event_handlers = [
        dp.message_handlers,
        dp.edited_message_handlers,
        dp.callback_query_handlers,
    ]

    dp.filters_factory.bind(IsAdminFilter, event_handlers=event_handlers)
    dp.filters_factory.bind(Access_Filter, event_handlers=event_handlers)
    dp.filters_factory.bind(IsUserFilter, event_handlers=event_handlers)