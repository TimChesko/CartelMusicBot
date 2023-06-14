from aiogram import Router
from . import registration

router = Router()
router.include_router(registration.reg_nickname)
