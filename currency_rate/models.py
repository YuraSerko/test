from django.db import models
import requests
from currency.settings import api_id
import time

# Create your models here.
class Currencies(models.Model):
    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length = 100, null=True, blank=True) 
    api_name = models.CharField(max_length = 100) #openexchangerates.org
    popular = models.IntegerField(null=True, blank=True)
    
    @staticmethod #start from script
    def create_currency_list():     #the will be exceptions and create instead of save()???
        q=5
        t=5
        while q>0:
            try:
                popular_dict = {'USD':1, 'EUR':2, 'GBP':3,  'JPY':4 ,'CHF':5, 'AUD':6, u'CAD':7, 'RUB':8 }
                address = 'http://openexchangerates.org/api/latest.json?app_id=' + api_id
                address_names = 'http://openexchangerates.org/api/currencies.json'
                while t>0:
                    r = requests.get(address)
                    r_names = requests.get(address_names)
                    if r.status_code==200 and r_names.status_code ==200:
                        t=0
                    else:
                        print 'bad status'
                        time.sleep(10)
                        t-=1
                for key in r.json()[u'rates']:
                    for key_names in r_names.json().keys():
                        if key == key_names:
                            for i in popular_dict.keys():
                                if key_names.rstrip() == i:
                                    cur = Currencies(api_name = key, name = r_names.json()[key_names], popular=popular_dict[i])
                                    break
                                else:
                                    cur = Currencies(api_name = key, name = r_names.json()[key_names], popular = 0)
                            cur.save()
                q=0
            except requests.exceptions.ConnectionError:
                print 'no conn'
                time.sleep(10)
                q-=1




    class Meta:
        db_table = 'currencies'
        

        
class CurrencyRate(models.Model):
    id = models.AutoField(primary_key = True)
    value = models.DecimalField(max_digits=12, decimal_places=6)
    current_day_date = models.DateTimeField(auto_now = True, null=True)
    currencies = models.ForeignKey(Currencies, unique = True)
    
    class Meta:
        db_table = 'currency_rate'
        