from django.db import models


class User(models.Model):
    username = models.CharField(max_length=150)
    tg_id = models.PositiveIntegerField()
    last_msg = models.TextField(blank=True, null=True)
    subscribe = models.BooleanField(default=False)
    register_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class QuestionAnswer(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    text = models.TextField()


class Setting(models.Model):
    tg_key = models.CharField(max_length=256)
    prompt = models.TextField()
    chat_gpt_version = models.CharField(default='text-davinci-003', max_length=156)
    openai_organization = models.CharField(max_length=256)
    openai_api_key = models.CharField(max_length=256)
    trial_days = models.PositiveIntegerField(default=1)
