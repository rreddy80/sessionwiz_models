from django.conf.urls import patterns, include, url
from django.views.generic.list import ListView

from example.forms import ContactForm1, ContactForm2, ContactForm3
from example import views
from example.views import ContactWizard, StatementView
from example.models import Model1

formslist = [ContactForm1, ContactForm2, ContactForm3]


urlpatterns = patterns('',
    url(r'^contact/$',
        StatementView.as_view(),
        name='contact_list'),
    url(r'^contact/add/$',
        ContactWizard.as_view(formslist),
        name='contact_add'),
    url(r'^contact/edit/(?P<statement_id>[-\d]+)$',
        'example.views.edit_wizard',
        name='contact_edit'),
    #url(r'^contact/edit/(?P<statement_id>[-\d]+)$',
    #    ContactWizard.as_view(formslist),
    #    name='contact_edit'),
    url(r'^contact/submit/$', views.submit_wizard, name='submit_confirm'),
)
