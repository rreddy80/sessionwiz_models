from django import forms
from example.models import Model1, Model2, Model3

class ContactForm1(forms.ModelForm):

    class Meta:
        model = Model1
        fields = [
            'id',
            'subject',
            ]
        
class ContactForm2(forms.ModelForm):

    class Meta:
        model = Model1
        fields = [
            'sender',
            ]
        
class ContactForm3(forms.ModelForm):

    class Meta:
        model = Model1
        fields = [
            'message',
            'amt_paid',
            ]
