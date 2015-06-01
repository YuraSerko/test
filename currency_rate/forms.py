# -*- coding=utf-8 -*-
from django import forms
from currency_rate.models import Currencies, CurrencyRate

class ConvertForm(forms.Form):
    currency1 = forms.ChoiceField()
    currency2 = forms.ChoiceField()    
    summa = forms.FloatField(required=False)
           
    
    def __init__(self, *args, **kwargs):
        super(ConvertForm, self).__init__(*args, **kwargs)
        currency_choice = []
        for i in Currencies.objects.all():
                currency_choice.append((i.api_name, i.name))
        self.fields['currency1'].choices = currency_choice
        self.fields['currency2'].choices = currency_choice
    
    
    def clean_summa(self):
        summa = self.cleaned_data['summa']
        if summa is None:
            self._errors["summa"] = "<div class='form_err text-error' >Заполните все поля</div>"
        return summa
    