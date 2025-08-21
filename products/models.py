from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify


class Category(models.Model):
    """
    Catégorie de produits/services
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nom de la catégorie'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Description'
    )
    
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        verbose_name='Slug'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Catégorie active'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Dernière modification'
    )
    
    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """
    Modèle pour les produits et services
    """
    
    # Types de produits
    TYPE_CHOICES = [
        ('product', 'Produit'),
        ('service', 'Service'),
    ]
    
    # Informations de base
    name = models.CharField(
        max_length=200,
        verbose_name='Nom du produit/service'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Description'
    )
    
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Catégorie'
    )
    
    product_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='product',
        verbose_name='Type'
    )
    
    # Prix et taxes
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Prix unitaire (HT)'
    )
    
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=18.00,
        validators=[MinValueValidator(0)],
        verbose_name='Taux de TVA (%)'
    )
    
    # Gestion du stock (pour les produits physiques)
    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name='Quantité en stock'
    )
    
    min_stock_level = models.PositiveIntegerField(
        default=0,
        verbose_name='Niveau d\'alerte stock'
    )
    
    # Informations supplémentaires
    sku = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Code SKU'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Produit actif'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Dernière modification'
    )
    
    class Meta:
        verbose_name = 'Produit/Service'
        verbose_name_plural = 'Produits/Services'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def price_with_tax(self):
        """Calcule le prix TTC"""
        return self.unit_price * (1 + self.tax_rate / 100)
    
    @property
    def tax_amount(self):
        """Calcule le montant de la TVA"""
        return self.unit_price * (self.tax_rate / 100)
    
    @property
    def stock_status(self):
        """Retourne le statut du stock"""
        if self.product_type == 'service':
            return 'N/A'
        elif self.stock_quantity <= 0:
            return 'Rupture'
        elif self.stock_quantity <= self.min_stock_level:
            return 'Faible'
        else:
            return 'Disponible'
    
    def is_low_stock(self):
        """Vérifie si le stock est faible"""
        return self.stock_quantity <= self.min_stock_level
    
    def is_out_of_stock(self):
        """Vérifie si le produit est en rupture de stock"""
        return self.stock_quantity <= 0
