from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from orders.models import Order
from customers.models import Customer


class Invoice(models.Model):
    """
    Modèle pour la gestion des factures
    """
    
    # Statuts de facturation
    STATUS_CHOICES = [
        ('pending', 'En attente de paiement'),
        ('partially_paid', 'Partiellement payée'),
        ('paid', 'Payée'),
        ('cancelled', 'Annulée'),
        ('overdue', 'En retard'),
    ]
    
    # Informations de base
    invoice_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Numéro de facture'
    )
    
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='invoice',
        verbose_name='Commande'
    )
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='invoices',
        verbose_name='Client'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Statut'
    )
    
    # Dates importantes
    invoice_date = models.DateField(
        default=timezone.now,
        verbose_name='Date de facture'
    )
    
    due_date = models.DateField(
        verbose_name='Date d\'échéance'
    )
    
    paid_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Date de paiement'
    )
    
    # Montants
    subtotal_ht = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Sous-total HT'
    )
    
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Montant TVA'
    )
    
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Montant total TTC'
    )
    
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Montant payé'
    )
    
    remaining_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Montant restant dû'
    )
    
    # Informations de facturation
    payment_terms = models.CharField(
        max_length=100,
        default='30 jours',
        verbose_name='Conditions de paiement'
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notes'
    )
    
    # Métadonnées
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Dernière modification'
    )
    
    class Meta:
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'
        ordering = ['-invoice_date']
    
    def __str__(self):
        return f"Facture {self.invoice_number} - {self.customer}"
    
    def save(self, *args, **kwargs):
        # Génération automatique du numéro de facture
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        
        # Calcul automatique des montants
        self.calculate_amounts()
        
        # Calcul automatique de la date d'échéance
        if not self.due_date:
            self.due_date = self.calculate_due_date()
        
        super().save(*args, **kwargs)
    
    def generate_invoice_number(self):
        """Génère un numéro de facture unique"""
        from datetime import datetime
        prefix = "FAC"
        date_str = datetime.now().strftime("%Y%m%d")
        # Trouver le dernier numéro pour aujourd'hui
        today_invoices = Invoice.objects.filter(
            invoice_date=datetime.now().date()
        ).count()
        sequence = today_invoices + 1
        return f"{prefix}{date_str}{sequence:03d}"
    
    def calculate_amounts(self):
        """Calcule les montants de la facture"""
        # Récupération des montants depuis la commande
        self.subtotal_ht = self.order.subtotal_ht
        self.tax_amount = self.order.tax_amount
        self.total_amount = self.order.total_amount
        
        # Calcul du montant restant dû
        self.remaining_amount = self.total_amount - self.paid_amount
    
    def calculate_due_date(self):
        """Calcule la date d'échéance basée sur les conditions de paiement"""
        if '30 jours' in self.payment_terms:
            return self.invoice_date + timezone.timedelta(days=30)
        elif '15 jours' in self.payment_terms:
            return self.invoice_date + timezone.timedelta(days=15)
        elif '7 jours' in self.payment_terms:
            return self.invoice_date + timezone.timedelta(days=7)
        else:
            return self.invoice_date + timezone.timedelta(days=30)
    
    def is_overdue(self):
        """Vérifie si la facture est en retard"""
        if self.status in ['paid', 'cancelled']:
            return False
        return timezone.now().date() > self.due_date
    
    def is_fully_paid(self):
        """Vérifie si la facture est entièrement payée"""
        return self.paid_amount >= self.total_amount
    
    def get_payment_percentage(self):
        """Retourne le pourcentage de paiement"""
        if self.total_amount == 0:
            return 0
        return (self.paid_amount / self.total_amount) * 100
    
    def mark_as_paid(self, amount=None):
        """Marque la facture comme payée"""
        if amount:
            self.paid_amount += amount
        else:
            self.paid_amount = self.total_amount
        
        self.paid_date = timezone.now().date()
        self.remaining_amount = self.total_amount - self.paid_amount
        
        # Mise à jour du statut
        if self.is_fully_paid():
            self.status = 'paid'
        elif self.paid_amount > 0:
            self.status = 'partially_paid'
        
        self.save()
    
    def get_status_display_color(self):
        """Retourne la couleur CSS pour le statut"""
        status_colors = {
            'pending': 'warning',
            'partially_paid': 'info',
            'paid': 'success',
            'cancelled': 'danger',
            'overdue': 'danger',
        }
        return status_colors.get(self.status, 'secondary')
    
    def get_days_overdue(self):
        """Retourne le nombre de jours de retard"""
        if self.is_overdue():
            return (timezone.now().date() - self.due_date).days
        return 0
