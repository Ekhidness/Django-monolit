# polls/admin.py

from django.contrib import admin
from .models import Question, Choice, UserProfile, Vote

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'birth_date']
    search_fields = ['user__username']

admin.site.register(Question, QuestionAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Vote)
