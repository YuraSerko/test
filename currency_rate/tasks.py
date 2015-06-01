# coding=utf-8
import sys, os
from celery.task.schedules import crontab
from celery.decorators import periodic_task
import urllib, urllib2, cookielib
import time
from django.conf import settings
import requests
from currency.settings import api_id
from currency_rate.models import Currencies, CurrencyRate
from django.db import models
from django.core.wsgi import get_wsgi_application
#import datetime
import os
import sys
from django.core.wsgi import get_wsgi_application
os.environ['DJANGO_SETTINGS_MODULE'] = 'currency.settings'
application = get_wsgi_application()




@periodic_task(run_every=crontab(minute="1"))
def my_task():
    address = 'http://openexchangerates.org/api/latest.json?app_id=' + api_id
    q=5
    t=5
    while q>0:
        try:
            while t>0:
                r = requests.get(address)
                if r.status_code==200:
                    t=0
                else:
                    print 'bad status'
                    time.sleep(10)
                    t-=1
            for key in r.json()[u'rates']:
                print key.rstrip(),":",
                r.json()[u'rates'][key]
                cur = Currencies.objects.get(api_name = key) #if not add
                try:
                    cr_obj = CurrencyRate.objects.get(currencies=cur)
                    cr_obj.value = r.json()[u'rates'][key]
                    cr_obj.save()
                except CurrencyRate.DoesNotExist:
                    cur_rate = CurrencyRate(value = r.json()[u'rates'][key], currencies = cur)
                    cur_rate.save()
            q=0
        except requests.exceptions.ConnectionError:
            print 'no conn'
            time.sleep(10)
            q-=1
    
    #obj, created = CurrencyRate.objects.update_or_create(value = r.json()[u'rates'][key], defaults = {'currencies' : cur } )
    