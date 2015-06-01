from django.contrib import admin

# Register your models here.
from models import CurrencyRate, Currencies

class CurrenciesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'api_name', 'popular')
    search_fields = ('api_name',)
      
    

class CurrencyRateAdmin(admin.ModelAdmin):
    list_display = ('id', 'value')
    search_fields = ('id',)
        
admin.site.register(CurrencyRate, CurrencyRateAdmin)
admin.site.register(Currencies, CurrenciesAdmin)