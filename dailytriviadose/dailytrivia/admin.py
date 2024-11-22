from django.contrib import admin
from .models import User, Trivia, TriviaGameRecord, UserTriviaDates

class TriviaAdmin(admin.ModelAdmin):
    list_display = ('title', 'url')
    search_fields = ('title',)

admin.site.register(User)
admin.site.register(Trivia)
admin.site.register(TriviaGameRecord)
admin.site.register(UserTriviaDates)