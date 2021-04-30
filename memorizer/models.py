from django.db import models
from django.contrib.auth.models import User


class Word(models.Model):
    eng_word = models.CharField(max_length=100)
    rus_word = models.CharField(max_length=100)
    transcription_uk = models.CharField(max_length=100)
    transcription_us = models.CharField(max_length=100)
    editor = models.ForeignKey(User, on_delete=models.CASCADE)


#
#
# class WordProgress(models.Model):
#     word = models.ForeignKey(Words, on_delete=models.CASCADE)
#     repeats = models.IntegerField()
#     mistakes = models.IntegerField()
#     percent = models.DecimalField(max_digits=2, decimal_places=0)
#     user = models.ManyToManyField(User)


class MemorizingList(models.Model):
    completed = models.BooleanField(default=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)


class MemorizingLine(models.Model):
    link = models.ForeignKey(MemorizingList, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    completes = models.IntegerField()
    fails = models.IntegerField()
#
#
# class MemoryListRepeats(models.Model):
#     date = models.DateField(auto_now=True)
#     percent = models.IntegerField()
