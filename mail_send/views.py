from django.shortcuts import render
from mail_send.models import MailSender
from mail_send.forms import MailerForm
from django.views.generic import CreateView, ListView
from django.http import HttpResponse,HttpResponseRedirect
from django.conf import settings
from django.template import loader
from django.urls import reverse_lazy  
from django.core.mail import BadHeaderError, send_mail
import threading
import time
# Create your views here.

class MailView(CreateView):
    model = MailSender
    form_class = MailerForm
    template_name = "index.html"
    success_url = '/mails_list'


def send_email(mail):
    subject = mail.subject
    message = mail.message
    to_email = mail.to_email
    delay = mail.delay
    if subject and message and to_email and delay:
        try:
            print("Письмо {} будет отправленно через {} секунду/секунд".format(subject, delay))
            time.sleep(delay)
            mail.status = True
            mail.save()
            send_mail(subject, message, settings.EMAIL_HOST_USER, [to_email])
            print("Письмо {} отправленно".format(subject))
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
    else:
        return HttpResponse('Проверьте, все ли поля заполнены правильно.')


def mails_list(request):
    template = loader.get_template('mails_list.html')
    mails = MailSender.objects.all()
    mails.order_by('delay')
    mails_count = mails.count()
    threads = []
    max_mails = mails.count() - 10
    if max_mails < 0:
        max_mails = 0
    if mails_count > 10:
        mails_count = 10
    for mail in mails:
        if not mail.status:
            t = threading.Thread(target=send_email, args=(mail,))
            threads.append(t)
            t.start()
    if mails_count > 1:
        mails_data = {
            "title": "{} отправленных писем".format(mails_count),
            "mails": mails[max_mails:],
        }
    else:
        mails_data = {
            "title": "{} отправленное письмо ".format(mails_count),
            "mails": mails[max_mails:],
        }
    return HttpResponse(template.render(mails_data, request))    

    for t in threads:
        t.join()