import os
import django
import logging
import openai
from aiogram import Bot, Dispatcher, executor, types
from django.core.management.base import BaseCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from telegram.models import User, Setting, Question, Answer, Message

setting = Setting.objects.all().last()

openai.organization = setting.openai_organization
openai.api_key = setting.openai_api_key

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rest.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=setting.tg_key)

dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    try:
        hello_msg = Message.objects.get(id=1).text
    except Message.DoesNotExist:
        hello_msg = "Привет! Я бот."
    try:
        User.objects.get(tg_id=message.from_user.id)
    except User.DoesNotExist:
        User.objects.create(username=message.from_user.username, tg_id=message.from_user.id)
    await message.answer(hello_msg)


@dp.message_handler()
async def chat(message: types.Message):
    try:
        error_mgs = Message.objects.get(id=1).text
    except Message.DoesNotExist:
        error_mgs = "Произошла ошибка при обработке вашего запроса"
    setting = Setting.objects.all().last()
    user = User.objects.get(tg_id=message.from_user.id)
    try:
        if user.last_msg is not None:
            final_msg = user.last_msg + '\n' + message.text
        else:
            final_msg = message.text
        response = openai.Completion.create(
            engine=setting.chat_gpt_version,
            prompt=final_msg,
            max_tokens=2000
        )
        Question.objects.create(user=user, text=final_msg)
        Answer.objects.create(user=user, text=response.choices[0].text)
        user.last_msg = response.choices[0].text
        user.save()
        await message.answer(response.choices[0].text)

    except Exception as e:
        print(e)
        await message.answer(error_mgs)


class Command(BaseCommand):
    help = 'Старт ТГ-бота'

    def handle(self, *args, **options):
        executor.start_polling(dp, skip_updates=True)
