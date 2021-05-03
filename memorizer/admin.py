from django.contrib import admin
from memorizer.models import Word, MemorizingList, MemorizingLine, Statistics

admin.site.register(Word)
admin.site.register(MemorizingList)
admin.site.register(MemorizingLine)
admin.site.register(Statistics)
