from django.contrib import admin
from mail_send.models import MailSender
# Register your models here.

@admin.register(MailSender)
class mailAdmin(admin.ModelAdmin):
    pass