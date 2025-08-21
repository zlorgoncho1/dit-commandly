from django import forms
from django.utils import timezone
from invoices.models import Invoice
from orders.models import Order
from customers.models import Customer


class InvoiceForm(forms.ModelForm):
    """
    Formulaire pour la création et modification des factures
    """
    
    class Meta:
        model = Invoice
        fields = [
            'order', 'customer', 'status', 'due_date',
            'payment_terms', 'notes'
        ]
        widgets = {
            'order': forms.Select(attrs={
                'class': 'form-select',
                'id': 'order_select'
            }),
            'customer': forms.Select(attrs={
                'class': 'form-select',
                'id': 'customer_select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': timezone.now().date().isoformat()
            }),
            'payment_terms': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes sur la facture (optionnel)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les commandes qui n'ont pas encore de facture
        if not self.instance.pk:
            existing_invoices = Invoice.objects.values_list('order_id', flat=True)
            self.fields['order'].queryset = Order.objects.exclude(
                id__in=existing_invoices
            ).filter(status__in=['confirmed', 'in_progress', 'ready', 'delivered'])
        else:
            # Pour la modification, inclure la commande actuelle
            self.fields['order'].queryset = Order.objects.filter(
                id__in=[self.instance.order.id] + list(
                    Order.objects.exclude(
                        id__in=Invoice.objects.values_list('order_id', flat=True)
                    ).values_list('id', flat=True)
                )
            )
        
        # Filtrer les clients actifs
        self.fields['customer'].queryset = Customer.objects.filter(is_active=True)
        
        # Limiter les statuts selon le contexte
        if self.instance.pk:
            current_status = self.instance.status
            if current_status == 'paid':
                # Si payée, on ne peut que la laisser en l'état
                self.fields['status'].choices = [
                    choice for choice in Invoice.STATUS_CHOICES 
                    if choice[0] == 'paid'
                ]
            elif current_status == 'cancelled':
                # Si annulée, on ne peut que la laisser en l'état
                self.fields['status'].choices = [
                    choice for choice in Invoice.STATUS_CHOICES 
                    if choice[0] == 'cancelled'
                ]
        
        # Personnaliser les choix de conditions de paiement
        self.fields['payment_terms'].choices = [
            ('7 jours', '7 jours'),
            ('15 jours', '15 jours'),
            ('30 jours', '30 jours'),
            ('45 jours', '45 jours'),
            ('60 jours', '60 jours'),
        ]
    
    def clean(self):
        cleaned_data = super().clean()
        order = cleaned_data.get('order')
        customer = cleaned_data.get('customer')
        due_date = cleaned_data.get('due_date')
        
        # Validation : cohérence client-commande
        if order and customer and order.customer != customer:
            self.add_error('customer', 'Le client de la facture doit correspondre au client de la commande.')
        
        # Validation : date d'échéance dans le futur
        if due_date and due_date <= timezone.now().date():
            self.add_error('due_date', 'La date d\'échéance doit être dans le futur.')
        
        # Validation : commande avec des produits
        if order and not order.items.exists():
            self.add_error('order', 'La commande doit contenir au moins un produit.')
        
        return cleaned_data


class InvoiceSearchForm(forms.Form):
    """
    Formulaire de recherche de factures
    """
    
    SEARCH_CHOICES = [
        ('invoice_number', 'Numéro de facture'),
        ('customer', 'Client'),
        ('status', 'Statut'),
        ('date', 'Date'),
        ('amount', 'Montant'),
    ]
    
    search_type = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        initial='invoice_number',
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
    
    status = forms.ChoiceField(
        choices=[('', 'Tous les statuts')] + Invoice.STATUS_CHOICES,
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
    
    due_date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'style': 'max-width: 150px;'
        })
    )
    
    due_date_to = forms.DateField(
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
    
    payment_status = forms.ChoiceField(
        choices=[
            ('', 'Tous les statuts'),
            ('paid', 'Payées'),
            ('partially_paid', 'Partiellement payées'),
            ('pending', 'En attente'),
            ('overdue', 'En retard')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 150px;'
        })
    )
