# Create your views here.
# coding: utf-8
from django.shortcuts import render
from django.views.generic import TemplateView
from currency_rate.models import Currencies, CurrencyRate
from currency_rate.forms import ConvertForm
from django.views.generic.edit import FormView
from lib.decorators import render_to
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.cache import cache_page
from django.core.cache import cache
import json
#====================================================================================================================================================== 
def conversion(rate_dict):
    result = float(rate_dict['amount'])*float(rate_dict['cur2v']/rate_dict['cur1v'])
    return result
#======================================================================================================================================================
def conversion_no_obj(rate_dict):
    success = True
    try:
        temp = float(rate_dict['amount'])
    except ValueError:
        success = False
        result = dict({'1': 'amount must be a number'})
        return success, result
    result = float(rate_dict['amount'])*float(rate_dict['cur2v']/rate_dict['cur1v'])
    return success, result
#======================================================================================================================================================
class Converse:
    def __init__(self, **kwargs):
        print 'INIT'
        self.currency_code_1= kwargs['currency_code_1']
        self.currency_code_2 = kwargs['currency_code_2']
        self.amount = kwargs['amount']
    
    def get_rate(self):
        rate_dict = {}
        success = True
        i=1
        try:
            c1 = Currencies.objects.get(api_name=self.currency_code_1)
            c2 = Currencies.objects.get(api_name=self.currency_code_2)
            try:
                cur1 = CurrencyRate.objects.get(currencies__api_name=self.currency_code_1)
                cur2 = CurrencyRate.objects.get(currencies__api_name=self.currency_code_2)
            except CurrencyRate.DoesNotExist:
                    success = False 
                    rate_dict[i] = 'no rate'
                    i+=1
        except:
            success = False 
            rate_dict[i] = 'no such currency'
            i+=1
        amount = self.amount
        try:
            temp = float(amount)
        except ValueError:
            success = False
            rate_dict[i] = 'amount must be number'
        if success == True: #no errors
            #write to cash if no errors
            cache.set('cur1', [self.currency_code_1, cur1.value, cur1.currencies.name], 30) #simple list 
            cache.set('cur2', [self.currency_code_2, cur2.value, cur2.currencies.name], 30) #simple list 
            rate_dict = dict({'cur1':c1.name, 'cur2':c2.name, 'cur1v':cur1.value, 'cur2v':cur2.value, 'amount':amount}) 
        return success, rate_dict
    
    def do_convertion(self): # on exit always   result (if no errors), rate_dict (errors or enter data), success
        if not cache.get('cur1') and not cache.get('cur2'): #no cash go to base
            #print 'get from base'
            success, rate_dict = self.get_rate() #get from base   - objs, amount
            if success == True:
                result = conversion(rate_dict)
                return result, rate_dict, success #result, dict, success
            else:
                return None, rate_dict, success #errors
        else:
            #print 'without base'
            c1 = cache.get('cur1')
            c2 = cache.get('cur2')
            if c1[0] == self.currency_code_1 and c2[0] == self.currency_code_2: #api_names are the same
                rate_dict =({'cur1':c1[2], 'cur2':c2[2], 'cur1v':c1[1], 'cur2v':c2[1],'amount':self.amount })
                success, result = conversion_no_obj(rate_dict)
                if success == True:
                    return result, rate_dict, success
                else:
                    rate_dict = result
                    return None, rate_dict, success
                    
            else:
                #print 'without base but not the same = > base'
                success, rate_dict = self.get_rate() #get from base   - objs, amount
                if success == True:
                    result = conversion(rate_dict)
                    return result, rate_dict, success
                else:
                    return None,rate_dict, success


#======================================================================================================================================================
@render_to('convert.html')
def convert(request):
    context = {}
    if request.method == 'POST':
        form = ConvertForm(request.POST)
        if form.is_valid():
            #amount=form.cleaned_data['summa'])#orig
            amount= str(form.cleaned_data['summa']).decode('utf-8') #if amount whatever you want
            currency1= form.cleaned_data['currency1']#api_name1
            currency2= form.cleaned_data['currency2']#api_name2
            redirect_url = reverse('api_html', kwargs = {'currency_code_1': currency1, 'currency_code_2': currency2, 'amount':amount,})
            return HttpResponseRedirect(redirect_url)
        else:
            form = ConvertForm(request.POST)
    else:
        form = ConvertForm()
    context['form'] = form
    context['basic_courses'] = CurrencyRate.objects.filter(currencies__popular__gt=0).order_by('currencies__popular')
    context['api_html'] = True
    return context
#======================================================================================================================================================
class ApiConvertHTML(TemplateView):
    template_name = 'api.html'
    def post(self, request, **kwargs):
        form = ConvertForm(request.POST)
        if form.is_valid():
            amount= str(form.cleaned_data['summa']).decode('utf-8') #if amount whatever you want
            currency1= form.cleaned_data['currency1']#api_name1
            currency2= form.cleaned_data['currency2']#api_name2
            redirect_url = reverse('api_html', kwargs = {'currency_code_1': currency1, 'currency_code_2': currency2, 'amount':amount})
            return HttpResponseRedirect(redirect_url)
        else:
            amount= str(form.cleaned_data['summa']).decode('utf-8') #if amount whatever you want
            currency1= form.cleaned_data['currency1']#api_name1
            currency2= form.cleaned_data['currency2']#api_name2
            if amount == None:
                amount = 0 #js validate
            redirect_url = reverse('api_html', kwargs = {'currency_code_1': currency1, 'currency_code_2': currency2, 'amount':amount})
            return HttpResponseRedirect(redirect_url)

           
    def get_context_data(self, **kwargs):
        context = super(ApiConvertHTML, self).get_context_data(**kwargs)
        context['form'] = ConvertForm()
        context['currency_code_1'] = kwargs['currency_code_1']
        context['currency_code_2'] = kwargs['currency_code_2']
        context['amount'] = kwargs['amount']
        #result, rate_dict, success = do_convertion(**kwargs)#or
        new_obj = Converse(**kwargs)
        result, rate_dict, success = new_obj.do_convertion() 
        if success:
            context['result'] = str(rate_dict['amount'])+ rate_dict['cur1']+'='+str(result)+ rate_dict['cur2']
        else:
            res_str = 'Error:'
            for k in rate_dict.keys():
                res_str+='<br>' + rate_dict[k]
            context['result'] = res_str
        context['api_html'] = True 
        return context

#======================================================================================================================================================
class ApiConvertText(TemplateView):
    template_name = 'api.html'
    def get_context_data(self, **kwargs):
        context = super(ApiConvertText, self).get_context_data(**kwargs)
        #result, rate_dict, success = do_convertion(**kwargs) #original
        new_obj = Converse(**kwargs)
        result, rate_dict, success = new_obj.do_convertion() 
        if success:
            context['result'] = str(rate_dict['amount'])+ rate_dict['cur1']+'='+str(result)+ rate_dict['cur2']
        else:
            res_str = 'Error:'
            for k in rate_dict.keys():
                res_str+='<br>' + rate_dict[k]
            context['result'] = res_str
        context['api_text'] = True
        return context

#======================================================================================================================================================
class ApiConvertJSON(TemplateView):
    template_name = 'api.html'
    def get_context_data(self, **kwargs):
        context = super(ApiConvertJSON, self).get_context_data(**kwargs)
        #result, rate_dict, success = do_convertion(**kwargs)#or
        new_obj = Converse(**kwargs)
        result, rate_dict, success = new_obj.do_convertion() 
        result_string_dict = {}
        if success:
            result_string_dict['success'] ='True'
            result_string_dict['result'] =result 
        else:
            result_string_dict['success'] ='False'
            result_string_dict['error'] =rate_dict
        json_str = json.dumps(result_string_dict)    
        context['result'] = json_str
        context['api_json'] = True
        return context   
#======================================================================================================================================================      
def calc_cross(st,nd, usd):
    cross = round(st.value/usd.value*usd.value/nd.value,3)
    return cross    
#======================================================================================================================================================
#cross curses
class CrossCurses(TemplateView):
    template_name = 'cross_curses.html'
    print 'cross curses'
    def get_context_data(self, **kwargs):
        context = super(CrossCurses, self).get_context_data(**kwargs)
        popular_rates = CurrencyRate.objects.filter(currencies__popular__gt=0).order_by('currencies__popular')
        #print popular_rates.count() #maybe length
        #usd rate
        usd_rate = CurrencyRate.objects.get(currencies__api_name = 'USD')
        all_cross_course_dict = {}
        counter = 0
        while counter<popular_rates.count():
            print popular_rates[counter] # 1st currency
            list_name = []
            list_val= []
            list_assembly = []
            # cross for every currency
            popular_rates_minus_one = CurrencyRate.objects.filter(currencies__popular__gt=0).exclude(id=popular_rates[counter].id).order_by('currencies__popular')
            for po in popular_rates_minus_one:
                list_name.append(po.currencies.api_name)
                cross = calc_cross(popular_rates[counter], po, usd_rate)
                list_val.append(cross)
            list_assembly= [list_name, list_val]
            all_cross_course_dict[popular_rates[counter]] = list_assembly
            counter+=1
        context['popular_rates'] = popular_rates
        context['all_cross_course_dict'] = all_cross_course_dict
        return context    

#======================================================================================================================================================      
class AllRate(TemplateView):
    template_name = 'all_rate.html'
    def get_context_data(self, **kwargs):
        context = super(AllRate, self).get_context_data(**kwargs)
        rates =  CurrencyRate.objects.all()
        my_dict = {}
        st =0
        e = 7
        i = 1
        while e<rates.count()+7:
            my_dict[i] = rates[st:e]
            st=e
            e+=7
            i+=1
        context['rates'] = my_dict
        return context    