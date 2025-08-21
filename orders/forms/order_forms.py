from django import forms
from django.core.validators import MinValueValidator
from django.utils import timezone
from orders.models import Order, OrderItem
from customers.models import Customer
from products.models import Product


class OrderForm(forms.ModelForm):
    """
    Formulaire pour la création et modification des commandes
    """
    
    class Meta:
        model = Order
        fields = [
            'customer', 'status', 'expected_delivery_date',
            'notes'
        ]
        widgets = {
            'customer': forms.Select(attrs={
                'class': 'form-select',
                'id': 'customer_select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'expected_delivery_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': timezone.now().date().isoformat()
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes sur la commande (optionnel)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les clients actifs
        self.fields['customer'].queryset = Customer.objects.filter(is_active=True)
        
        # Limiter les statuts selon le contexte
        if self.instance.pk:
            current_status = self.instance.status
            if current_status == 'delivered':
                # Si livrée, on ne peut que clôturer ou annuler
                self.fields['status'].choices = [
                    choice for choice in Order.STATUS_CHOICES 
                    if choice[0] in ['delivered', 'closed', 'cancelled']
                ]
            elif current_status == 'cancelled':
                # Si annulée, on ne peut que clôturer
                self.fields['status'].choices = [
                    choice for choice in Order.STATUS_CHOICES 
                    if choice[0] in ['cancelled', 'closed']
                ]
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        expected_delivery_date = cleaned_data.get('expected_delivery_date')
        
        # Validation : date de livraison prévue dans le futur
        if expected_delivery_date and expected_delivery_date < timezone.now().date():
            self.add_error('expected_delivery_date', 'La date de livraison prévue doit être dans le futur.')
        
        # Validation : statut de livraison cohérent
        if status == 'delivered' and not self.instance.delivered_date:
            # Si on marque comme livrée, on met à jour la date de livraison
            cleaned_data['delivered_date'] = timezone.now().date()
        
        return cleaned_data


class OrderItemForm(forms.ModelForm):
    """
    Formulaire pour les lignes de commande
    """
    
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'unit_price', 'tax_rate', 'notes']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-select product-select',
                'id': 'product_select'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control quantity-input',
                'min': '1',
                'step': '1',
                'placeholder': '1'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control price-input',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'tax_rate': forms.NumberInput(attrs={
                'class': 'form-control tax-input',
                'step': '0.01',
                'min': '0',
                'placeholder': '18.00'
            }),
            'notes': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Notes sur cette ligne (optionnel)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les produits actifs
        self.fields['product'].queryset = Product.objects.filter(is_active=True)
        
        # Rendre les champs prix et TVA en lecture seule si c'est une modification
        if self.instance.pk:
            self.fields['unit_price'].widget.attrs['readonly'] = True
            self.fields['tax_rate'].widget.attrs['readonly'] = True
    
    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        unit_price = cleaned_data.get('unit_price')
        product = cleaned_data.get('product')
        
        # Validation : quantité positive
        if quantity and quantity <= 0:
            self.add_error('quantity', 'La quantité doit être strictement positive.')
        
        # Validation : prix unitaire positif
        if unit_price and unit_price <= 0:
            self.add_error('unit_price', 'Le prix unitaire doit être strictement positif.')
        
        # Validation : stock disponible pour les produits physiques
        if product and product.product_type == 'product' and quantity:
            if quantity > product.stock_quantity:
                self.add_error('quantity', f'Stock insuffisant. Disponible : {product.stock_quantity}')
        
        return cleaned_data


class OrderSearchForm(forms.Form):
    """
    Formulaire de recherche de commandes
    """
    
    SEARCH_CHOICES = [
        ('order_number', 'Numéro de commande'),
        ('customer', 'Client'),
        ('status', 'Statut'),
        ('date', 'Date'),
    ]
    
    search_type = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        initial='order_number',
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
        choices=[('', 'Tous les statuts')] + Order.STATUS_CHOICES,
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
