from aiogram import Router
from . import listening, my_tracks

router = Router()
router.include_router(listening.track_menu)
router.include_router(listening.new_track)
router.include_router(listening.old_track)
router.include_router(my_tracks.my_tracks_menu)
router.include_router(my_tracks.rejected_tracks)

