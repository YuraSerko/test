from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
#from currency_rate.views import CurrencyList, Convert
#from currency_rate.views import Convert
from currency_rate.views import ApiConvertText, ApiConvertJSON, CrossCurses, ApiConvertHTML, AllRate


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'messages_tape.views.home', name='home'),
    # url(r'^messages_tape/', include('messages_tape.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    
   
)

urlpatterns += patterns('currency_rate.views',
    url(r'^$', 'convert', name = 'convert'), 
    
    # whatever you want amount
    url(r'^(?P<amount>\w+[\.\w+]*)/(?P<currency_code_1>\w+)/to/(?P<currency_code_2>\w+)/in/text/$', ApiConvertText.as_view()),
    url(r'^(?P<amount>\w+[\.\w+]*)/(?P<currency_code_1>\w+)/to/(?P<currency_code_2>\w+)/in/html/$', ApiConvertHTML.as_view(), name = "api_html"),
    url(r'^(?P<amount>\w+[\.\w+]*)/(?P<currency_code_1>\w+)/to/(?P<currency_code_2>\w+)/in/json/$', ApiConvertJSON.as_view()),
    
   
#     only number where amount
#     url(r'^(?P<amount>\d+[\.\d+]*)/(?P<currency_code_1>\w+)/to/(?P<currency_code_2>\w+)/in/text/$', ApiConvertText.as_view()),
#     url(r'^(?P<amount>\d+[\.\d+]*)/(?P<currency_code_1>\w+)/to/(?P<currency_code_2>\w+)/in/html/$', ApiConvertHTML.as_view(), name = "api_html"),
#     url(r'^(?P<amount>\d+[\.\d+]*)/(?P<currency_code_1>\w+)/to/(?P<currency_code_2>\w+)/in/json/$', ApiConvertJSON.as_view()),
    
    
    url(r'^cross_curses/$', CrossCurses.as_view(), name = 'cross_curses'),
    url(r'^all_rate/$', AllRate.as_view(), name = 'all_rate'),
   
)
