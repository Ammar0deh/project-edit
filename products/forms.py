from django import forms
from products.models import Client, Cart

class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ['payment_code',]
        widgets = {            
             
            'payment_code': forms.TextInput(attrs={
                'class':"form-control",
                'id':"payment_code",
                'placeholder': 'Payment Code'
            }),}
    
class ClientForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
                'class':"form-control",
                'id':"first_name",
            }))
    last_name = forms.CharField(max_length=30, required=True,widget=forms.TextInput(attrs={
                'class':"form-control",
                'id':"last_name",
            }))

    class Meta:
        model = Client
        fields = ['phone_number', 'address', 'last_name', 'first_name']
        widgets = {            
             
                 
            'address': forms.TextInput(attrs={
                'class':"form-control",
                'id':"address",
            }),
            'phone_number': forms.TextInput(attrs={
                'class':"form-control",
                'id':"phone_number",
            }),
        }


    def save(self, commit=True):
        client = super(ClientForm, self).save(commit=False)

        client.user.first_name = self.cleaned_data['first_name']
        client.user.last_name = self.cleaned_data['last_name']
        client.user.save()

        if commit:
            client.save()

        return client
    
    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            self.fields['first_name'].widget.attrs['placeholder'] = instance.user.first_name
            self.fields['last_name'].widget.attrs['placeholder'] = instance.user.last_name
