from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncEngine
from structlog._log_levels import BoundLoggerFilteringAtDebug

from src.data import config
from src.models.tracks import TrackHandler
from src.models.user import UserHandler

router = Router()


@router.callback_query(F.data.startswith('listening_'))
async def taking_task(callback: CallbackQuery, bot: Bot, engine: AsyncEngine,
                      database_logger: BoundLoggerFilteringAtDebug):
    data = callback.data.split('_')
    track_id = int(callback.data.split('_')[2])
    user_id, title = await TrackHandler(engine, database_logger).get_task_info_by_id(track_id)
    nickname = await UserHandler(engine, database_logger).get_user_nickname_by_tg_id(user_id)
    # await bot.edit_message_caption(caption='Поменял текст', chat_id=config.CHATS_BACKUP[0], message_id=msg_id)
    match data:
        case _, 'approve', __:
            await callback.message.edit_caption(caption=f'✅ОДОБРЕНО✅ \n'
                                                        f'Трек: {title} \n'
                                                        f'Артист: {nickname} \n'
                                                        f'Одобрил: {callback.from_user.id} / @{callback.from_user.username}',
                                                reply_markup=None)
            await TrackHandler(engine, database_logger).set_track_to_approve(track_id, callback.from_user.id)
            await bot.send_message(user_id, f'Ваш трек "{title}" одобрен! \n'
                                            f'Он добавлен в раздел "Треки" \n'
                                            f'Чтобы перейти в этот раздел пройдите "Моя музыка" ---> "Треки" ---> Выберите трек')
        case _, 'approve-promo', __:
            await callback.message.edit_caption(caption=f'✅ОДОБРЕНО С ПРОМО✅ \n'
                                                        f'Трек: {title} \n'
                                                        f'Артист: {nickname} \n'
                                                        f'Одобрил: {callback.from_user.id} / @{callback.from_user.username}',
                                                reply_markup=None)
            await TrackHandler(engine, database_logger).set_track_to_approve_promo(track_id, callback.from_user.id)
            await bot.send_message(user_id, f'Ваш трек "{title}" одобрен с доступом к промо! \n'
                                            f'Он добавлен в раздел "Треки" \n'
                                            f'К каждому треку нужно заполнять информацию\n'
                                            f'Чтобы это сделать перейдите из главного меню в: \n'
                                            f'"Моя музыка" ---> "Треки" ---> Выберите трек')
