from aiogram import Router

from src.dialogs.my_studio.release import dialogs

router = Router()

router.include_routers(dialogs.create_new_release,
                       dialogs.feat_releases,
                       dialogs.lvl1_page,
                       dialogs.choose_tracks,
                       dialogs.lvl2_page,
                       dialogs.lvl3_page)
