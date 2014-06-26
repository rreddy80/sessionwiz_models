# Create your views here.
from collections import OrderedDict
from django.shortcuts import render_to_response, get_object_or_404, HttpResponseRedirect
from django.contrib.formtools.wizard.views import SessionWizardView
from django.contrib.formtools.wizard.forms import ManagementForm
from django.contrib.formtools.wizard import storage
from django.contrib.formtools.wizard.storage import get_storage
from django.forms.models import model_to_dict
from django.core.mail import send_mail
from django.views.generic.list import ListView
from django.template import RequestContext
import datetime
import logging

logr = logging.getLogger(__name__)

from example.models import Model1, Model2, Model3, statement_progress
from example.forms import ContactForm1, ContactForm2, ContactForm3

from wizards.session import SessionWizard

formlist = [ContactForm1, ContactForm2, ContactForm3]

def percentage(part, whole):
    return round(100 * float(part)/float(whole), 2)


def get_dict_values(given_context):
    result_dict = {'0': {'subject': given_context['subject']
                           },
                     '1': {'sender': given_context['sender'],
                           },
                     '2': {'message': given_context['message'],
                           'amt_paid': given_context['amt_paid'],
                           },
                     }
    return result_dict


class StatementView(ListView):
    model = Model1
    paginate_by = '10'

    def get_context_data(self, **kwargs):
        context = super(StatementView, self).get_context_data(**kwargs)
        context['now'] = datetime.datetime.now()
        return context


class ContactWizard(SessionWizardView):
    #instance = None
    #template_name = 'wizard.html'

    def get_template_names(self):
        if not self.steps.next:
            return 'preview.html'
        else:
            return 'wizard.html'

    def get_context_data(self, form, **kwargs):
        context = super(ContactWizard, self).get_context_data(form=form, **kwargs)
        #logr.debug("current step: " + str(self.steps.current))
        #logr.debug("total #steps: " + str(self.steps.count))
        context.update({'percent_complete': percentage(self.steps.current,self.steps.count)})
        if not self.steps.next:
            context.update({'uname': 'Ramesh Reddy'})
        return context

    def done(self, form_list, **kwargs):
        try:
            #logr.debug("Before fetching statementid - - Reddy")
            #logr.debug(form_list[0].cleaned_data)
            #logr.debug(form_list[1].cleaned_data)
            #logr.debug(form_list[2].cleaned_data)
            #logr.debug(self.initial_dict)
            #logr.debug("id from dict:" + str(self.initial_dict['0']['id']))
            #logr.debug("id from form_list:" + str(form_list[0].cleaned_data))
            #statementid = form_list[0].cleaned_data['id']
            #statementid = self.kwargs['statement_id']
            statementid = self.initial_dict['0']['id']
            statement = get_object_or_404(Model1, pk=statementid)
            instance = statement
        except:
            statement = None
            instance = Model1()

        # process form data here
        for form in form_list:
            logr.debug(form)
            logr.debug(form_list)
            if not form is None:
                if isinstance(form, dict):
                    for field, value in form.iteritems():   # for field, value in form.cleaned_data.iteritems():
                        setattr(instance, field, value)
                else:
                    for field, value in form.cleaned_data.iteritems():
                        setattr(instance, field, value)
        instance.save()

        #
        #logr.debug("below is the new/ existing id")
        #logr.debug(instance.id)
        
        #form_data = [form.cleaned_data for form in form_list]

        # lets grab some session data
        #logr.debug("--------------------- * START * SESSION DATA ---------------------")
        #for key in ('form_data', 'wizard_id'):
        #    if key in self.request.session:
        #        logr.debug(self.request.session[key])
        #logr.debug("--------------------- * END * SESSION DATA ---------------------")

        # lets grab WizardView.get_all_cleaned_data()
        logr.debug("--------------------- * START * all cleaned data from all forms ---------")
        logr.debug(self.get_all_cleaned_data())
        logr.debug("--------------------- * END * all cleaned data from all forms ---------")
        
        #submissions = Model1.objects.all()
        # lets grab data off the current instance
        #logr.debug("--------- grabbing current instance ---------")
        this_statement = Model1.objects.get(pk=instance.id)
        #logr.debug(this_statement)
        #logr.debug(this_statement.id)
        #logr.debug(this_statement.subject)
        #logr.debug(this_statement.sender)
        #logr.debug(this_statement.amt_paid)

        context_final = model_to_dict(this_statement)
        logr.debug(context_final)
        
        return render_to_response('done.html', {
            'thissubmission': context_final,
            #'form_data': form_data,
            #'submissions': submissions,            
        })
    

    def post(self, *args, **kwargs):
        """
        This method handles POST requests.

        The wizard will render either the current step (if form validation
        wasn't successful), the next step (if the current step was stored
        successful) or the done view (if no more steps are available)
        """
        if 'save_comeback_later' in self.request.POST:
             if self.request.POST['save_comeback_later']:
                # get form_data from all the forms
                final_forms = OrderedDict()
                for form_key in self.get_form_list():
##                    form_obj = self.get_form(step=form_key,
##                                             data=self.storage.get_step_data(form_key),
##                                             files=self.storage.get_step_files(form_key))
##                    #form_obj = self.get_form(data=self.request.POST, files=self.request.FILES)    
##                    #logr.debug("list of forms data - " + str(form_key) + ": " + str(form_obj))
##                    if not form_obj.is_valid():
##                        logr.debug("INVALID DATA FOUND, calling revalidation failure")
##                        logr.debug(self.get_all_cleaned_data())
##                        logr.debug(form_obj)
##                        return self.render_revalidation_failure(form_key, form_obj, **kwargs)
                    form_obj = self.get_cleaned_data_for_step(form_key)
                    final_forms[form_key] = form_obj
                #logr.debug("value is TRUE")
                done_response = self.done(final_forms.values(), form_dict=final_forms, **kwargs)
                self.storage.reset()
                return done_response
        return super(ContactWizard, self).post(self, *args, **kwargs)


def edit_wizard(request, statement_id):
    statement = get_object_or_404(Model1, pk=statement_id)
    initial_values = {
        '0':
        {
            'subject': statement.subject,
            'id': statement.id,
            },
        '1':
        {
            'sender': statement.sender,
            },
        '2':
        {
            'message': statement.message,
            'amt_paid': statement.amt_paid,
            },
        }
    # return the wizard
    form = ContactWizard.as_view(formlist, initial_dict=initial_values)
    return form(context=RequestContext(request), request=request)


def submit_wizard(request):
    # something here that would update the model status to "Submitted"

    # and also create a csv file and store in amazon cloud

    # and also creae a pdf document from preview html page to pdf (use pisa)

    # finally, redirect the user to landing page
    return HttpResponseRedirect('/example/contact/')

'''
def quit_wizard(request):
    # save data in the current form
    try:
        statementid = currwizard.initial_dict['0']['id']
        statement = get_object_or_404(Model1, pk=statementid)
        instance = statement
    except:
        statement = None
        instance = Model1()

    # process form data here
    for form in ContactWizard.kwards(form_list):
        for field, value in form.cleaned_data.iteritems():
            setattr(instance, field, value)        
    instance.save()    

    # add a record in the progress step for this statement
    try:
        exist_statement = statement_progress.objects.get(statement=instance.id)
        exist_statement.current_step = currstep
        exist_statement.save()
    except:
        new_statement = statement_progress.objects.create(statement=statement_id,
                                                          current_step=currstep)
        new_statement.save()
    
    # return the user to landing page
    return HttpResponseRedirect('/example/contact/')


def process_form_data(form_list):
    form_data = [form.cleaned_data for form in form_list]

    logr.debug("subject:", form_data[0]['subject'])
    logr.debug("sender:", form_data[1]['sender'])
    logr.debug("message:", form_data[2]['message'])
    logr.debug("amt_paid:", form_data[2]['amt_paid'])

    m1 = Model1()
    for i in range(0,len(form_list)):
        for k,v in form_data[i].iteritems():
            setattr(m1, k, v)
    m1.save()

    m2 = Model2()
    for k,v in form_data[1].iteritems():
        setattr(m2, k, v)
    m2.save()

    m3 = Model3()
    for k,v in form_data[2].iteritems():
        setattr(m3, k, v)
    m3.save()

    return form_data

    send_mail(form_data[0]['subject'],
              form_data[1]['message'], form_data[0]['sender'],
              ['vramesh.reddy@gmail.com'], fail_silently = False)

# some new method overrides here
    def get_form_initial(self, step):
        if 'model1_id' in self.kwargs and step == 'stepname':
            statement_id = self.kwargs['model1_id']
            statement = Model1.objects.get(id=statement_id)
            from django.forms.models import model_to_dict
            statement_dict = model_to_dict(statement)
            return statement_dict
        else:
            return self.initial_dict.get(step, {})


    def get_form_instance(self, step):
        # return self.instance_dict.get(step, None)

        if self.instance is None:
            if 'model1_id' in self.kwargs:
                statement_id = self.kwargs['model1_id']
                self.instance = Model1.objects.get(id=statement_id)
            else:
                self.instance = Model1()
        return self.instance
'''
