from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from customers.models import Customer
from products.models import Product


class Order(models.Model):
    """
    Modèle pour la gestion des commandes
    """
    
    # Statuts de commande
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmée'),
        ('in_progress', 'En cours'),
        ('ready', 'Prête'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
        ('closed', 'Clôturée'),
    ]
    
    # Informations de base
    order_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Numéro de commande'
    )
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Client'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Statut'
    )
    
    # Dates importantes
    order_date = models.DateTimeField(
        default=timezone.now,
        verbose_name='Date de commande'
    )
    
    expected_delivery_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Date de livraison prévue'
    )
    
    delivered_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Date de livraison effective'
    )
    
    # Montants
    subtotal_ht = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Sous-total HT'
    )
    
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Montant TVA'
    )
    
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Montant total TTC'
    )
    
    # Informations supplémentaires
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notes'
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
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering = ['-order_date']
    
    def __str__(self):
        return f"Commande {self.order_number} - {self.customer}"
    
    def save(self, *args, **kwargs):
        # Génération automatique du numéro de commande
        if not self.order_number:
            self.order_number = self.generate_order_number()
        
        # Calcul automatique des montants
        self.calculate_totals()
        
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Génère un numéro de commande unique"""
        from datetime import datetime
        prefix = "CMD"
        date_str = datetime.now().strftime("%Y%m%d")
        # Trouver le dernier numéro pour aujourd'hui
        today_orders = Order.objects.filter(
            order_date__date=datetime.now().date()
        ).count()
        sequence = today_orders + 1
        return f"{prefix}{date_str}{sequence:03d}"
    
    def calculate_totals(self):
        """Calcule les totaux de la commande"""
        items = self.items.all()
        self.subtotal_ht = sum(item.line_total_ht for item in items)
        self.tax_amount = sum(item.line_tax_amount for item in items)
        self.total_amount = self.subtotal_ht + self.tax_amount
    
    def can_be_confirmed(self):
        """Vérifie si la commande peut être confirmée"""
        return self.status == 'draft' and self.items.exists()
    
    def can_be_delivered(self):
        """Vérifie si la commande peut être livrée"""
        return self.status in ['confirmed', 'in_progress', 'ready']
    
    def mark_as_delivered(self):
        """Marque la commande comme livrée"""
        if self.can_be_delivered():
            self.status = 'delivered'
            self.delivered_date = timezone.now().date()
            self.save()
    
    def get_status_display_color(self):
        """Retourne la couleur CSS pour le statut"""
        status_colors = {
            'draft': 'secondary',
            'confirmed': 'info',
            'in_progress': 'warning',
            'ready': 'primary',
            'delivered': 'success',
            'cancelled': 'danger',
            'closed': 'dark',
        }
        return status_colors.get(self.status, 'secondary')


class OrderItem(models.Model):
    """
    Ligne de commande
    """
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Commande'
    )
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Produit/Service'
    )
    
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Quantité'
    )
    
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Prix unitaire HT'
    )
    
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Taux de TVA (%)'
    )
    
    notes = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Notes'
    )
    
    class Meta:
        verbose_name = 'Ligne de commande'
        verbose_name_plural = 'Lignes de commande'
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity} - {self.order.order_number}"
    
    @property
    def line_total_ht(self):
        """Calcule le total HT de la ligne"""
        return self.unit_price * self.quantity
    
    @property
    def line_tax_amount(self):
        """Calcule le montant de TVA de la ligne"""
        return self.line_total_ht * (self.tax_rate / 100)
    
    @property
    def line_total_ttc(self):
        """Calcule le total TTC de la ligne"""
        return self.line_total_ht + self.line_tax_amount
    
    def save(self, *args, **kwargs):
        # Récupération automatique du prix et de la TVA du produit
        if not self.unit_price:
            self.unit_price = self.product.unit_price
        if not self.tax_rate:
            self.tax_rate = self.product.tax_rate
        
        super().save(*args, **kwargs)
        
        # Recalcul des totaux de la commande
        self.order.calculate_totals()
        self.order.save()
