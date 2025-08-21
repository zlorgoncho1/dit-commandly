from django.db import models
from django.utils import timezone
from decimal import Decimal


class DashboardMetrics(models.Model):
    """
    Modèle pour stocker les métriques du tableau de bord
    Permet de mettre en cache les calculs coûteux
    """
    
    # Période de calcul
    period_start = models.DateField(
        verbose_name='Début de période'
    )
    
    period_end = models.DateField(
        verbose_name='Fin de période'
    )
    
    # Métriques des commandes
    total_orders = models.PositiveIntegerField(
        default=0,
        verbose_name='Total des commandes'
    )
    
    pending_orders = models.PositiveIntegerField(
        default=0,
        verbose_name='Commandes en attente'
    )
    
    completed_orders = models.PositiveIntegerField(
        default=0,
        verbose_name='Commandes terminées'
    )
    
    cancelled_orders = models.PositiveIntegerField(
        default=0,
        verbose_name='Commandes annulées'
    )
    
    # Métriques financières
    total_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Chiffre d\'affaires total'
    )
    
    total_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total payé'
    )
    
    total_outstanding = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total restant dû'
    )
    
    # Métriques des clients
    total_customers = models.PositiveIntegerField(
        default=0,
        verbose_name='Total des clients'
    )
    
    new_customers = models.PositiveIntegerField(
        default=0,
        verbose_name='Nouveaux clients'
    )
    
    active_customers = models.PositiveIntegerField(
        default=0,
        verbose_name='Clients actifs'
    )
    
    # Métriques des produits
    total_products = models.PositiveIntegerField(
        default=0,
        verbose_name='Total des produits'
    )
    
    low_stock_products = models.PositiveIntegerField(
        default=0,
        verbose_name='Produits en stock faible'
    )
    
    out_of_stock_products = models.PositiveIntegerField(
        default=0,
        verbose_name='Produits en rupture'
    )
    
    # Métadonnées
    last_calculated = models.DateTimeField(
        auto_now=True,
        verbose_name='Dernier calcul'
    )
    
    is_current = models.BooleanField(
        default=True,
        verbose_name='Métriques actuelles'
    )
    
    class Meta:
        verbose_name = 'Métrique du tableau de bord'
        verbose_name_plural = 'Métriques du tableau de bord'
        ordering = ['-period_start']
        unique_together = ['period_start', 'period_end']
    
    def __str__(self):
        return f"Métriques {self.period_start} - {self.period_end}"
    
    @classmethod
    def get_current_metrics(cls):
        """Récupère les métriques actuelles"""
        today = timezone.now().date()
        return cls.objects.filter(
            period_start__lte=today,
            period_end__gte=today,
            is_current=True
        ).first()
    
    @classmethod
    def get_monthly_metrics(cls, year, month):
        """Récupère les métriques pour un mois donné"""
        from datetime import date
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timezone.timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timezone.timedelta(days=1)
        
        return cls.objects.filter(
            period_start=start_date,
            period_end=end_date
        ).first()
    
    @property
    def order_completion_rate(self):
        """Calcule le taux de complétion des commandes"""
        if self.total_orders == 0:
            return 0
        return (self.completed_orders / self.total_orders) * 100
    
    @property
    def payment_collection_rate(self):
        """Calcule le taux de recouvrement des paiements"""
        if self.total_revenue == 0:
            return 0
        return (self.total_paid / self.total_revenue) * 100
    
    @property
    def average_order_value(self):
        """Calcule la valeur moyenne des commandes"""
        if self.total_orders == 0:
            return Decimal('0.00')
        return self.total_revenue / self.total_orders
    
    @property
    def customer_retention_rate(self):
        """Calcule le taux de rétention des clients"""
        if self.total_customers == 0:
            return 0
        return (self.active_customers / self.total_customers) * 100


class TopCustomer(models.Model):
    """
    Modèle pour stocker les meilleurs clients
    """
    
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.CASCADE,
        verbose_name='Client',
        null=True,  # Temporairement nullable
        blank=True
    )
    
    total_orders = models.PositiveIntegerField(
        default=0,
        verbose_name='Total des commandes'
    )
    
    total_spent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total dépensé'
    )
    
    last_order_date = models.DateField(
        verbose_name='Date de dernière commande'
    )
    
    rank = models.PositiveIntegerField(
        verbose_name='Rang'
    )
    
    period_start = models.DateField(
        verbose_name='Début de période'
    )
    
    period_end = models.DateField(
        verbose_name='Fin de période'
    )
    
    class Meta:
        verbose_name = 'Meilleur client'
        verbose_name_plural = 'Meilleurs clients'
        ordering = ['rank']
        unique_together = ['customer', 'period_start', 'period_end']
    
    def __str__(self):
        return f"{self.customer} - Rang {self.rank}"


class TopProduct(models.Model):
    """
    Modèle pour stocker les meilleurs produits
    """
    
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        verbose_name='Produit',
        null=True,  # Temporairement nullable
        blank=True
    )
    
    total_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name='Quantité totale vendue'
    )
    
    total_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Revenus totaux'
    )
    
    total_orders = models.PositiveIntegerField(
        default=0,
        verbose_name='Nombre de commandes'
    )
    
    rank = models.PositiveIntegerField(
        verbose_name='Rang'
    )
    
    period_start = models.DateField(
        verbose_name='Début de période'
    )
    
    period_end = models.DateField(
        verbose_name='Fin de période'
    )
    
    class Meta:
        verbose_name = 'Meilleur produit'
        verbose_name_plural = 'Meilleurs produits'
        ordering = ['rank']
        unique_together = ['product', 'period_start', 'period_end']
    
    def __str__(self):
        return f"{self.product} - Rang {self.rank}"
