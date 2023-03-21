from django.contrib import admin
from telegram.models import User, Setting, Answer, Question, Message


@admin.register(User)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('username', 'tg_id', 'subscribe', 'register_date')
    search_fields = ('username', 'subscribe')


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('tg_key', 'prompt', 'trial_days', 'chat_gpt_version')


@admin.register(Answer)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('user', 'text', 'date')
    search_fields = ('user',)


@admin.register(Message)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'text')


@admin.register(Question)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('user', 'text', 'date')
    search_fields = ('user',)

# Register your models here.
