# -*- coding=UTF-8 -*-
import os
import sys
import requests
from currency.settings import api_id
from currency_rate.models import Currencies, CurrencyRate
from django.db import models
from django.core.wsgi import get_wsgi_application
import datetime
import time

os.environ['DJANGO_SETTINGS_MODULE'] = 'currency_rate.settings'
application = get_wsgi_application()


print 'st'
Currencies.create_currency_list()
print 'e'



        







