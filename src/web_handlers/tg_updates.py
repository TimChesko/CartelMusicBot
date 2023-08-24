import secrets

import aiohttp.web
import aiojobs
from aiogram import Bot, Dispatcher, types
from aiohttp import web

from src.data.config import load_config, Config

config: Config = load_config()
tg_updates_app = web.Application()


async def process_update(upd: types.Update, bot: Bot, dp: Dispatcher):
    await dp.feed_webhook_update(bot, upd)


async def execute(req: web.Request) -> web.Response:
    if not secrets.compare_digest(
        req.headers.get("X-Telegram-Bot-Api-Secret-Token", ""),
        config.webhook.token,
    ):
        raise aiohttp.web.HTTPNotFound()
    if not secrets.compare_digest(req.match_info["token"], config.tg.token):
        raise aiohttp.web.HTTPNotFound()
    scheduler: aiojobs.Scheduler = req.app["scheduler"]
    if scheduler.pending_count >= config.webhook.max_updates_in_queue:
        raise web.HTTPTooManyRequests()
    if scheduler.closed:
        raise web.HTTPServiceUnavailable(reason="Closed queue")
    await scheduler.spawn(
        process_update(
            types.Update(**(await req.json())), req.app["bot"], req.app["dp"]
        )
    )
    return web.Response()


tg_updates_app.add_routes([web.post("/bot/{token}", execute)])
