from aiogram import Router
from . import listening, my_tracks, rejected_tracks

router = Router()
router.include_router(listening.listening_menu)
router.include_router(listening.new_track)
router.include_router(listening.edit_track)
router.include_router(my_tracks.my_tracks_menu)
router.include_router(rejected_tracks.reloading_on_listening)

