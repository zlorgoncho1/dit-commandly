from django import forms
from django.core.validators import MinValueValidator
from django.utils import timezone
from payments.models import Payment
from invoices.models import Invoice
from customers.models import Customer


class PaymentForm(forms.ModelForm):
    """
    Formulaire pour la création et modification des paiements
    """
    
    class Meta:
        model = Payment
        fields = [
            'invoice', 'customer', 'amount', 'payment_method',
            'status', 'payment_date', 'transaction_id',
            'reference', 'notes'
        ]
        widgets = {
            'invoice': forms.Select(attrs={
                'class': 'form-select',
                'id': 'invoice_select'
            }),
            'customer': forms.Select(attrs={
                'class': 'form-select',
                'id': 'customer_select'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'payment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'max': timezone.now().date().isoformat()
            }),
            'transaction_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ID de transaction (optionnel)'
            }),
            'reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Référence (optionnel)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes sur le paiement (optionnel)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les factures non payées
        if not self.instance.pk:
            self.fields['invoice'].queryset = Invoice.objects.filter(
                status__in=['pending', 'partially_paid']
            ).exclude(status='cancelled')
        else:
            # Pour la modification, inclure la facture actuelle
            self.fields['invoice'].queryset = Invoice.objects.filter(
                id__in=[self.instance.invoice.id] + list(
                    Invoice.objects.filter(
                        status__in=['pending', 'partially_paid']
                    ).exclude(status='cancelled').values_list('id', flat=True)
                )
            )
        
        # Filtrer les clients actifs
        self.fields['customer'].queryset = Customer.objects.filter(is_active=True)
        
        # Limiter les statuts selon le contexte
        if self.instance.pk:
            current_status = self.instance.status
            if current_status == 'completed':
                # Si complété, on ne peut que le laisser en l'état
                self.fields['status'].choices = [
                    choice for choice in Payment.STATUS_CHOICES 
                    if choice[0] == 'completed'
                ]
            elif current_status == 'cancelled':
                # Si annulé, on ne peut que le laisser en l'état
                self.fields['status'].choices = [
                    choice for choice in Payment.STATUS_CHOICES 
                    if choice[0] == 'cancelled'
                ]
        
        # Personnaliser les choix de méthodes de paiement
        self.fields['payment_method'].choices = [
            ('mobile_money', 'Mobile Money'),
            ('cash', 'Espèces'),
            ('check', 'Chèque'),
            ('bank_transfer', 'Virement bancaire'),
            ('card', 'Carte bancaire'),
            ('paypal', 'PayPal'),
            ('other', 'Autre'),
        ]
    
    def clean(self):
        cleaned_data = super().clean()
        invoice = cleaned_data.get('invoice')
        customer = cleaned_data.get('customer')
        amount = cleaned_data.get('amount')
        payment_date = cleaned_data.get('payment_date')
        
        # Validation : cohérence client-facture
        if invoice and customer and invoice.customer != customer:
            self.add_error('customer', 'Le client du paiement doit correspondre au client de la facture.')
        
        # Validation : montant positif
        if amount and amount <= 0:
            self.add_error('amount', 'Le montant doit être strictement positif.')
        
        # Validation : montant ne dépasse pas le montant restant dû
        if invoice and amount:
            remaining_amount = invoice.remaining_amount
            if amount > remaining_amount:
                self.add_error('amount', f'Le montant ne peut pas dépasser le montant restant dû ({remaining_amount}€).')
        
        # Validation : date de paiement dans le passé ou aujourd'hui
        if payment_date and payment_date > timezone.now().date():
            self.add_error('payment_date', 'La date de paiement ne peut pas être dans le futur.')
        
        # Validation : cohérence facture-paiement
        if invoice and invoice.status == 'cancelled':
            self.add_error('invoice', 'Impossible de créer un paiement pour une facture annulée.')
        
        return cleaned_data


class PaymentSearchForm(forms.Form):
    """
    Formulaire de recherche de paiements
    """
    
    SEARCH_CHOICES = [
        ('payment_number', 'Numéro de paiement'),
        ('customer', 'Client'),
        ('invoice', 'Facture'),
        ('status', 'Statut'),
        ('method', 'Méthode'),
        ('date', 'Date'),
    ]
    
    search_type = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        initial='payment_number',
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
    
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.filter(is_active=True),
        required=False,
        empty_label="Tous les clients",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 200px;'
        })
    )
    
    invoice = forms.ModelChoiceField(
        queryset=Invoice.objects.all(),
        required=False,
        empty_label="Toutes les factures",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 200px;'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'Tous les statuts')] + Payment.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 150px;'
        })
    )
    
    payment_method = forms.ChoiceField(
        choices=[('', 'Toutes les méthodes')] + Payment.PAYMENT_METHOD_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 150px;'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'style': 'max-width: 150px;'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'style': 'max-width: 150px;'
        })
    )
    
    amount_min = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Montant min',
            'step': '0.01',
            'style': 'max-width: 120px;'
        })
    )
    
    amount_max = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Montant max',
            'step': '0.01',
            'style': 'max-width: 120px;'
        })
    )
