from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from invoices.models import Invoice
from users.models import CustomUser


class Payment(models.Model):
    """
    Modèle pour la gestion des paiements
    """
    
    # Modes de paiement
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Espèces'),
        ('mobile_money', 'Mobile Money'),
        ('check', 'Chèque'),
        ('bank_transfer', 'Virement bancaire'),
        ('card', 'Carte bancaire'),
        ('paypal', 'PayPal'),
        ('other', 'Autre'),
    ]
    
    # Statuts de paiement
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
        ('refunded', 'Remboursé'),
    ]
    
    # Informations de base
    payment_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Numéro de paiement'
    )
    
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Facture'
    )
    
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Client'
    )
    
    # Montants et méthodes
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Montant'
    )
    
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='Méthode de paiement'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Statut'
    )
    
    # Dates importantes
    payment_date = models.DateField(
        default=timezone.now,
        verbose_name='Date de paiement'
    )
    
    processed_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Date de traitement'
    )
    
    # Informations de transaction
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='ID de transaction'
    )
    
    reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Référence'
    )
    
    # Informations supplémentaires
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notes'
    )
    
    # Métadonnées
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments_created',
        verbose_name='Créé par'
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
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Paiement {self.payment_number} - {self.amount}€ - {self.customer}"
    
    def save(self, *args, **kwargs):
        # Génération automatique du numéro de paiement
        if not self.payment_number:
            self.payment_number = self.generate_payment_number()
        
        # Mise à jour automatique du statut
        if self.status == 'completed' and not self.processed_date:
            self.processed_date = timezone.now()
        
        super().save(*args, **kwargs)
        
        # Mise à jour de la facture associée
        self.update_invoice_payment()
    
    def generate_payment_number(self):
        """Génère un numéro de paiement unique"""
        from datetime import datetime
        prefix = "PAY"
        date_str = datetime.now().strftime("%Y%m%d")
        # Trouver le dernier numéro pour aujourd'hui
        today_payments = Payment.objects.filter(
            payment_date=datetime.now().date()
        ).count()
        sequence = today_payments + 1
        return f"{prefix}{date_str}{sequence:03d}"

    def update_invoice_payment(self):
        """Met à jour le paiement de la facture associée"""
        if self.status == 'completed':
            self.invoice.mark_as_paid(self.amount)
    
    def can_be_processed(self):
        """Vérifie si le paiement peut être traité"""
        return self.status == 'pending'
    
    def can_be_cancelled(self):
        """Vérifie si le paiement peut être annulé"""
        return self.status in ['pending', 'completed']
    
    def mark_as_completed(self):
        """Marque le paiement comme complété"""
        if self.can_be_processed():
            self.status = 'completed'
            self.processed_date = timezone.now()
            self.save()
    
    def mark_as_failed(self):
        """Marque le paiement comme échoué"""
        if self.status == 'pending':
            self.status = 'failed'
            self.save()
    
    def mark_as_cancelled(self):
        """Marque le paiement comme annulé"""
        if self.can_be_cancelled():
            self.status = 'cancelled'
            self.save()
    
    def get_status_display_color(self):
        """Retourne la couleur CSS pour le statut"""
        status_colors = {
            'pending': 'warning',
            'completed': 'success',
            'failed': 'danger',
            'cancelled': 'secondary',
            'refunded': 'info',
        }
        return status_colors.get(self.status, 'secondary')
    
    @property
    def is_fully_processed(self):
        """Vérifie si le paiement est entièrement traité"""
        return self.status == 'completed' and self.processed_date is not None
    
    def get_payment_method_display_icon(self):
        """Retourne l'icône pour la méthode de paiement"""
        method_icons = {
            'cash': 'fa-money-bill',
            'check': 'fa-university',
            'bank_transfer': 'fa-exchange-alt',
            'card': 'fa-credit-card',
            'paypal': 'fa-paypal',
            'other': 'fa-question-circle',
        }
        return method_icons.get(self.payment_method, 'fa-question-circle')
