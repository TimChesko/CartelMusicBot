from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler(timezone='Europe/Moscow')


async def scheduler_start():
    print("Hello")


def setup():
    scheduler.add_job(scheduler_start, 'interval', seconds=30)
    scheduler.start()
