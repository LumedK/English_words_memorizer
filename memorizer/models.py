from django.db import models
from django.contrib.auth.models import User


class Word(models.Model):
    eng_word = models.CharField(max_length=100)
    rus_word = models.CharField(max_length=100)
    transcription_uk = models.CharField(max_length=100)
    transcription_us = models.CharField(max_length=100)
    editor = models.ForeignKey(User, on_delete=models.CASCADE)


class MemorizingList(models.Model):
    completed = models.BooleanField(default=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)


class MemorizingLine(models.Model):
    link = models.ForeignKey(MemorizingList, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)


class Statistics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    list = models.ForeignKey(MemorizingList, on_delete=models.CASCADE)
    line = models.ForeignKey(MemorizingLine, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    run = models.IntegerField()
    completed = models.IntegerField(default=0)
    failed = models.IntegerField(default=0)
    user_text = models.CharField(max_length=100)
    date = models.DateField(auto_now=True)
