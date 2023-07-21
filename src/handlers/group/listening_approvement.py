from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import async_sessionmaker
from structlog._log_levels import BoundLoggerFilteringAtDebug

from src.models.tracks import TrackHandler
from src.models.user import UserHandler

router = Router()


@router.callback_query(F.data.startswith('listening_'))
async def taking_task(callback: CallbackQuery, bot: Bot, session_maker: async_sessionmaker,
                      database_logger: BoundLoggerFilteringAtDebug):
    data = callback.data.split('_')
    track_id = int(callback.data.split('_')[2])
    user_id, title = await TrackHandler(session_maker, database_logger).get_task_info_by_id(track_id)
    nickname, username = await UserHandler(session_maker, database_logger).get_nicknames_by_tg_id(user_id)
    # await bot.edit_message_caption(caption='Поменял текст', chat_id=config.CHATS_BACKUP[0], message_id=msg_id)
    match data:
        case _, 'approve', __:
            await callback.message.edit_caption(caption=f'✅ОДОБРЕНО✅ \n'
                                                        f'Серийный номер: #{track_id} \n'
                                                        f'Трек: "{title}" \n'
                                                        f'Артист: {nickname} / @{username} \n'
                                                        f'Одобрил: {callback.from_user.id} / @{callback.from_user.username}',
                                                reply_markup=None)
            await TrackHandler(session_maker, database_logger).set_new_status_track(track_id, 'approve', callback.from_user.id)
            await bot.send_message(user_id, f'Ваш трек "{title}" одобрен! \n'
                                            f'Он добавлен в раздел "Треки" \n'
                                            f'Чтобы перейти в этот раздел пройдите'
                                            f' "Моя музыка" ---> "Треки" ---> Выберите трек')
        case _, 'approve-edit', __:
            await callback.message.edit_caption(caption=f'ПОВТОРНОЕ ПРОСЛУШИВАНИЕ \n'
                                                        f'✅ОДОБРЕНО✅ \n'
                                                        f'Серийный номер: #{track_id} \n'
                                                        f'Трек: "{title}" \n'
                                                        f'Артист: {nickname} / @{username} \n'
                                                        f'Одобрил: {callback.from_user.id} / @{callback.from_user.username}',
                                                reply_markup=None)
            await TrackHandler(session_maker, database_logger).set_new_status_track(track_id, 'approve',
                                                                             callback.from_user.id)
            await bot.send_message(user_id, f'Ваш трек "{title}" одобрен! \n'
                                            f'Он добавлен в раздел "Треки" \n'
                                            f'Чтобы перейти в этот раздел пройдите'
                                            f' "Моя музыка" ---> "Треки" ---> Выберите трек')
        case _, 'approve-promo', __:
            await callback.message.edit_caption(caption=f'✅ОДОБРЕНО С ПРОМО✅ \n'
                                                        f'Серийный номер: #{track_id} \n'
                                                        f'Трек: "{title}" \n'
                                                        f'Артист: {nickname} / @{username} \n'
                                                        f'Одобрил: {callback.from_user.id} / @{callback.from_user.username}',
                                                reply_markup=None)
            await TrackHandler(session_maker, database_logger).set_new_status_track(track_id, 'approve_promo',
                                                                             callback.from_user.id)
            await bot.send_message(user_id, f'Ваш трек "{title}" одобрен с доступом к промо! \n'
                                            f'Он добавлен в раздел "Треки" \n'
                                            f'К каждому треку нужно заполнять информацию\n'
                                            f'Чтобы это сделать перейдите из главного меню в: \n'
                                            f'"Моя музыка" ---> "Треки" ---> Выберите трек')
        case _, 'approve-promo-edit', __:
            await callback.message.edit_caption(caption=f'ПОВТОРНОЕ ПРОСЛУШИВАНИЕ \n'
                                                        f'✅ОДОБРЕНО С ПРОМО✅ \n'
                                                        f'Серийный номер: #{track_id} \n'
                                                        f'Трек: "{title}" \n'
                                                        f'Артист: {nickname} / @{username} \n'
                                                        f'Одобрил: {callback.from_user.id} / @{callback.from_user.username}',
                                                reply_markup=None)
            await TrackHandler(session_maker, database_logger).set_new_status_track(track_id, 'approve_promo',
                                                                             callback.from_user.id)
            await bot.send_message(user_id, f'Ваш трек "{title}" одобрен с доступом к промо! \n'
                                            f'Он добавлен в раздел "Треки" \n'
                                            f'К каждому треку нужно заполнять информацию\n'
                                            f'Чтобы это сделать перейдите из главного меню в: \n'
                                            f'"Моя музыка" ---> "Треки" ---> Выберите трек')
        case _, 'pattern-reject', __:
            await callback.message.edit_reply_markup(reply_markup=markup_reject_patterns(track_id))
        case _, 'pattern-reject-edit', __:
            await callback.message.edit_reply_markup(reply_markup=markup_edit_reject_patterns(track_id))
        case _, 'reason-idiot', __:
            await callback.message.edit_caption(caption=f'⛔️ОТКЛОНЕНО⛔️ \n'
                                                        f'Серийный номер: #{track_id} \n'
                                                        f'Причина: Бездарный \n'
                                                        f'Трек: "{title}" \n'
                                                        f'Артист: {nickname} / @{username} \n'
                                                        f'Отклонил: {callback.from_user.id} / @{callback.from_user.username}',
                                                # TODO поменять @{callback.from_user.username} на запрос из бд с информацией о сотрудниках
                                                reply_markup=None)
            await TrackHandler(session_maker, database_logger).set_new_status_track(track_id, 'reject', callback.from_user.id)
            await bot.send_message(user_id, f'Ваш трек "{title}" отклонен( \n'
                                            f'Ну реально, иди поспи, сынок, музыка - не твое \n'
                                            f'Но если ты из тех кто не сдается и даже не знает, что такое матерый,'
                                            f' ты можешь переделать и отправить еще раз')
        case _, 'reason-idiot-edit', __:
            await callback.message.edit_caption(caption=f'ПОВТОРНОЕ ПРОСЛУШИВАНИЕ \n'
                                                        f'⛔️ОТКЛОНЕНО⛔️ \n'
                                                        f'Серийный номер: #{track_id} \n'
                                                        f'Причина: Бездарный \n'
                                                        f'Трек: "{title}" \n'
                                                        f'Артист: {nickname} / @{username} \n'
                                                        f'Отклонил: {callback.from_user.id} / @{callback.from_user.username}',
                                                # TODO поменять @{callback.from_user.username} на запрос из бд с информацией о сотрудниках
                                                reply_markup=None)
            await TrackHandler(session_maker, database_logger).set_new_status_track(track_id, 'reject', callback.from_user.id)
            await bot.send_message(user_id, f'Ваш трек "{title}" отклонен( \n'
                                            f'Ну реально, иди поспи, сынок, музыка - не твое \n'
                                            f'Но если ты из тех кто не сдается и даже не знает, что такое матерый,'
                                            f' ты можешь переделать и отправить еще раз')

        # case _, 'reason-mixing', __:
        # case _, 'reason-incorrect', __:
        # case _, 'reason-alrdy-was', __:
        case _, 'back-new', __:
            await callback.message.edit_reply_markup(reply_markup=markup_new_listening(track_id))
        case _, 'back-edit', __:
            await callback.message.edit_reply_markup(reply_markup=markup_edit_listening(track_id))
