from django import forms
from django.core.validators import MinValueValidator
from products.models import Product, Category


class CategoryForm(forms.ModelForm):
    """
    Formulaire pour la création et modification des catégories
    """
    
    class Meta:
        model = Category
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de la catégorie'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description de la catégorie (optionnel)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class ProductForm(forms.ModelForm):
    """
    Formulaire pour la création et modification des produits
    """
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category', 'product_type',
            'unit_price', 'tax_rate', 'stock_quantity', 'min_stock_level',
            'sku', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du produit/service'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description détaillée du produit/service'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'product_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'product_type'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'tax_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '18.00'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0',
                'id': 'stock_quantity'
            }),
            'min_stock_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0',
                'id': 'min_stock_level'
            }),
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Code SKU (optionnel)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Masquer les champs de stock pour les services
        if self.instance.pk and self.instance.product_type == 'service':
            self.fields['stock_quantity'].widget.attrs['style'] = 'display: none;'
            self.fields['min_stock_level'].widget.attrs['style'] = 'display: none;'
    
    def clean(self):
        cleaned_data = super().clean()
        product_type = cleaned_data.get('product_type')
        stock_quantity = cleaned_data.get('stock_quantity')
        min_stock_level = cleaned_data.get('min_stock_level')
        
        # Validation : stock requis pour les produits physiques
        if product_type == 'product':
            if stock_quantity is None or stock_quantity < 0:
                self.add_error('stock_quantity', 'La quantité en stock est requise et doit être positive.')
            if min_stock_level is None or min_stock_level < 0:
                self.add_error('min_stock_level', 'Le niveau d\'alerte stock est requis et doit être positif.')
        
        # Validation : prix unitaire positif
        unit_price = cleaned_data.get('unit_price')
        if unit_price and unit_price <= 0:
            self.add_error('unit_price', 'Le prix unitaire doit être strictement positif.')
        
        # Validation : taux de TVA positif
        tax_rate = cleaned_data.get('tax_rate')
        if tax_rate and tax_rate < 0:
            self.add_error('tax_rate', 'Le taux de TVA ne peut pas être négatif.')
        
        return cleaned_data


class ProductSearchForm(forms.Form):
    """
    Formulaire de recherche de produits
    """
    
    SEARCH_CHOICES = [
        ('name', 'Nom'),
        ('sku', 'SKU'),
        ('category', 'Catégorie'),
        ('description', 'Description'),
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
            'placeholder': 'Rechercher un produit...',
            'style': 'max-width: 300px;'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label="Toutes les catégories",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 200px;'
        })
    )
    
    product_type = forms.ChoiceField(
        choices=[('', 'Tous les types')] + Product.TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 150px;'
        })
    )
    
    price_min = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prix min',
            'step': '0.01',
            'style': 'max-width: 120px;'
        })
    )
    
    price_max = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prix max',
            'step': '0.01',
            'style': 'max-width: 120px;'
        })
    )
    
    stock_status = forms.ChoiceField(
        choices=[
            ('', 'Tous les statuts'),
            ('available', 'Disponible'),
            ('low', 'Stock faible'),
            ('out', 'Rupture')
        ],
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
