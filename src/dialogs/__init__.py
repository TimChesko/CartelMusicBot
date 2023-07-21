from aiogram import Router

from . import registrations, start, profile, admin, utils, my_studio, listening

router = Router()
router.include_router(my_studio.router)
router.include_router(admin.router)
router.include_router(start.start_menu)
router.include_router(registrations.router)
router.include_router(profile.router)
router.include_router(listening.router)
router.include_router(utils.router)
