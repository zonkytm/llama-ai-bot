from datetime import datetime, timedelta
import subprocess

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.exceptions import FileIsTooBig
import logging
import os
import command_list
import repository
import const
import aiohttp

async def send_weekly_message(dp):
    user_ids = await repository.get_all_users()
    for user_id in user_ids:
        try:
            await dp.bot.send_message(chat_id=user_id, text=const.ad_text)
        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")


# Создаем и настраиваем планировщик
scheduler = AsyncIOScheduler()


async def start_scheduler(dp):
    start_time = datetime.now() + timedelta(minutes=1)
    #scheduler.add_job(send_weekly_message, 'interval', days=1, args=[dp], start_date=start_time)
    scheduler.start()


async def start_command(message: types.Message):
    await repository.add_user(message.from_user.id)
    await message.answer(command_list.commands[command_list.Commands.start])
    await message.delete()

async def split_and_send_message(replycontent, message : types.Message):
    max_length = 4096
    for i in range (0, len(replycontent), max_length):
        await message.reply(replycontent[i: i+ max_length])

async def delete_command(message: types.Message):
    await message.delete()


async def handle_user_text_request(message: types.Message, bot):
    try:
        user_input = message.text
        if not user_input:
            await message.reply("Пожалуйста, введите текст для обработки.")
            return
        print(user_input)
        # Формируем URL и заголовки для API
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": "Bearer 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",
            "Content-Type": "application/json"
        }

        system_message = {
            "role": "system",
            "content": "Ты — профессиональный блогер, который пишет о путешествиях, образе жизни и технологиях. "
               "Твой стиль общения — дружелюбный и информативный. "
               "Если тебя спрашивают о чем-то, что не связано с блогерством, путешествиями, образом жизни или технологиями, "
               "отвечай, что это не твоя тематика."
        }
        # Формируем тело запроса
        payload = {
            "model": "deepseek/deepseek-r1:free",
            "messages": [
                system_message,
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        }

        # Отправляем запрос к API
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    await message.reply("Не удалось обработать запрос. Попробуйте позже.")
                    return

                # Обрабатываем ответ от API
                data = await response.json()
                reply_content = data.get("choices", [{}])[0].get("message", {}).get("content", "Ответ не получен.")

                # Отправляем ответ пользователю
                print(reply_content)
                # Отправляем ответ пользователю, разбивая его на части, если он слишком длинный
                await split_and_send_message(reply_content, message)

    except Exception as e:
        await message.reply("Произошла ошибка при обработке запроса. Попробуйте снова.")
        print(f"Ошибка: {e}")
  

async def send_waiting_sticker(message: types.Message, bot) -> types.Message:
    # Отправка стикера с песочными часами
    try:
        # Попытка отправить стикер с песочными часами
        sticker_message = await message.reply("⌛")
        return sticker_message
    except Exception as e:
        # Обработка любых других исключений, чтобы избежать прерывания работы
        logging.error(f"Ошибка при отправке стикера: {e}")
        text_message = await message.reply("Ожидайте...")
        return text_message

async def register_handlers(dp: Dispatcher, bot):
    dp.register_message_handler(start_command, commands=[command_list.Commands.start.value])
    dp.register_message_handler(lambda message: handle_user_text_request(message, bot),
                                content_types=types.ContentType.TEXT)
  
