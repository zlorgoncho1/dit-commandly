from django import forms
from django.core.validators import RegexValidator
from customers.models import Customer


class CustomerForm(forms.ModelForm):
    """
    Formulaire pour la création et modification des clients
    """

    
    class Meta:
        model = Customer
        fields = [
            'customer_type', 'first_name', 'last_name', 'company_name',
            'email', 'phone', 'address_line1', 'address_line2',
            'city', 'postal_code', 'country', 'tax_number',
            'ninea', 'is_active', 'notes'
        ]
        widgets = {
            'customer_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'customer_type'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de l\'entreprise (optionnel)',
                'id': 'company_name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemple.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+221769001942'
            }),
            'address_line1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Adresse principale'
            }),
            'address_line2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Complément d\'adresse (optionnel)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ville'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Code postal'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pays',
                'value': 'Sénégal'
            }),
            'tax_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro de TVA (optionnel)'
            }),
            'ninea': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro NINEA (optionnel)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes additionnelles (optionnel)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Masquer les champs entreprise si c'est un particulier
        if self.instance.pk:
            self.fields['company_name'].widget.attrs['style'] = (
                'display: none;' if self.instance.customer_type == 'individual' else ''
            )
    
    def clean(self):
        cleaned_data = super().clean()
        customer_type = cleaned_data.get('customer_type')
        company_name = cleaned_data.get('company_name')
        
        # Validation : nom d'entreprise requis pour les entreprises
        if customer_type == 'company' and not company_name:
            self.add_error('company_name', 'Le nom de l\'entreprise est requis pour les clients de type entreprise.')
        
        return cleaned_data


class CustomerSearchForm(forms.Form):
    """
    Formulaire de recherche de clients
    """
    
    SEARCH_CHOICES = [
        ('name', 'Nom'),
        ('email', 'Email'),
        ('phone', 'Téléphone'),
        ('company', 'Entreprise'),
        ('city', 'Ville'),
    ]
    
    search_type = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        initial='name',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 150px;'
        })
    )
    
    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher...',
            'style': 'max-width: 300px;'
        })
    )
    
    customer_type = forms.ChoiceField(
        choices=[('', 'Tous les types')] + Customer.TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 150px;'
        })
    )
    
    is_active = forms.ChoiceField(
        choices=[
            ('', 'Tous les statuts'),
            ('True', 'Actifs'),
            ('False', 'Inactifs')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 150px;'
        })
    )
