from aiogram import Router

from . import listening, tracks_menu, rejected, approved

router = Router()
router.include_router(listening.listening_menu)
router.include_router(listening.new_track)
router.include_router(listening.edit_track)
router.include_router(tracks_menu.my_tracks_menu)
router.include_router(rejected.reloading_on_listening)
router.include_router(approved.approved_filling_data)
