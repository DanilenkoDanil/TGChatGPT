import os
import django
import logging
import openai
from django.utils import timezone
from aiogram import Bot, Dispatcher, executor, types
from django.core.management.base import BaseCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from telegram.models import User, Setting, QuestionAnswer, Message

setting = Setting.objects.all().last()

openai.organization = setting.openai_organization
openai.api_key = setting.openai_api_key

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rest.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=setting.tg_key)

dp = Dispatcher(bot, storage=MemoryStorage())


def check_msg_exist(msg_id: int) -> bool:
    try:
        Message.objects.get(id=msg_id).text
        return True
    except Message.DoesNotExist:
        return False


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    if check_msg_exist(1):
        hello_msg = Message.objects.get(id=1).text
    else:
        hello_msg = "Привет! Я бот."
    try:
        User.objects.get(tg_id=message.from_user.id)
    except User.DoesNotExist:
        User.objects.create(username=message.from_user.username, tg_id=message.from_user.id)
    await message.answer(hello_msg)


@dp.message_handler()
async def chat(message: types.Message):
    setting = Setting.objects.all().last()
    try:
        user = User.objects.get(tg_id=message.from_user.id)
    except User.DoesNotExist:
        user = User.objects.create(username=message.from_user.username, tg_id=message.from_user.id)
    difference = timezone.now() - user.register_date
    if difference.days > setting.trial_days and user.subscribe is not True:
        if check_msg_exist(3):
            await message.answer(Message.objects.get(id=3).text)
        else:
            await message.answer('Ваша подписка окончена!')
        return
    if check_msg_exist(1):
        error_mgs = Message.objects.get(id=2).text
    else:
        error_mgs = "Произошла ошибка при обработке вашего запроса"
    user = User.objects.get(tg_id=message.from_user.id)

    try:
        if user.last_msg is not None:
            final_msg = setting.prompt + '\n' + 'Последнее сообщение:' + \
                        user.last_msg + '\n' + 'Текущее сообщение: ' + message.text
        else:
            final_msg = message.text
        response = openai.ChatCompletion.create(
            engine=setting.chat_gpt_version,
            prompt=final_msg,
            max_tokens=2000
        )
        QuestionAnswer.objects.create(user=user, question=final_msg, answer=response.choices[0].text)
        user.last_msg = message.text
        user.save()
        await message.answer(response.choices[0].text)

    except Exception as e:
        print(e)
        await message.answer(error_mgs)


class Command(BaseCommand):
    help = 'Старт ТГ-бота'

    def handle(self, *args, **options):
        executor.start_polling(dp, skip_updates=True)
