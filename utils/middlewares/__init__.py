from aiogram import Dispatcher

from .throttling import ThrottlingMiddleware


def setup(dispatcher: Dispatcher):
    dispatcher.middleware.setup(ThrottlingMiddleware(limit=0.2))
