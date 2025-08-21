from django.db import models
from django.core.validators import RegexValidator
from django.utils.text import slugify


class Customer(models.Model):
    """
    Modèle pour la gestion des clients
    """
    
    # Types de clients
    TYPE_CHOICES = [
        ('individual', 'Particulier'),
        ('company', 'Entreprise'),
    ]
    
    # Informations de base
    customer_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='individual',
        verbose_name='Type de client'
    )
    
    # Informations personnelles/entreprise
    first_name = models.CharField(
        max_length=50,
        verbose_name='Prénom'
    )
    
    last_name = models.CharField(
        max_length=50,
        verbose_name='Nom'
    )
    
    company_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Nom de l\'entreprise'
    )
    
    # Informations de contact
    email = models.EmailField(
        unique=True,
        verbose_name='Email'
    )
    
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+221[0-9]{9}$',
                message='Numéro de téléphone sénégalais invalide (ex: +221769001942)'
            )
        ],
        verbose_name='Téléphone'
    )
    
    # Adresse
    address_line1 = models.CharField(
        max_length=255,
        verbose_name='Adresse ligne 1'
    )
    
    address_line2 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Adresse ligne 2'
    )
    
    city = models.CharField(
        max_length=100,
        verbose_name='Ville'
    )
    
    postal_code = models.CharField(
        max_length=10,
        verbose_name='Code postal'
    )
    
    country = models.CharField(
        max_length=100,
        default='France',
        verbose_name='Pays'
    )
    
    # Informations commerciales
    tax_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Numéro de TVA'
    )
    
    ninea = models.CharField(
        max_length=14,
        blank=True,
        null=True,
        verbose_name='Numéro NINEA'
    )
    
    # Statut et métadonnées
    is_active = models.BooleanField(
        default=True,
        verbose_name='Client actif'
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notes'
    )
    
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        verbose_name='Slug'
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
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ['-created_at']
    
    def __str__(self):
        if self.customer_type == 'company' and self.company_name:
            return self.company_name
        return f"{self.first_name} {self.last_name}"
       
        
    def save(self, *args, **kwargs):
        if not self.slug:
            if self.customer_type == 'company' and self.company_name:
                self.slug = slugify(self.company_name)
            else:
                self.slug = slugify(f"{self.first_name}-{self.last_name}")
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        """Retourne le nom complet"""
        if self.customer_type == 'company' and self.company_name:
            return self.company_name
        return f"{self.first_name} {self.last_name}"
    
    @property
    def display_name(self):
        """Retourne le nom d'affichage"""
        if self.customer_type == 'company' and self.company_name:
            return f"{self.company_name} ({self.first_name} {self.last_name})"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_address(self):
        """Retourne l'adresse complète"""
        address_parts = [self.address_line1]
        if self.address_line2:
            address_parts.append(self.address_line2)
        address_parts.extend([self.postal_code, self.city, self.country])
        return ', '.join(filter(None, address_parts))
    
    def get_total_orders(self):
        """Retourne le nombre total de commandes"""
        from orders.models import Order
        return Order.objects.filter(customer=self).count()
    
    def get_total_spent(self):
        """Retourne le montant total dépensé"""
        from orders.models import Order
        orders = Order.objects.filter(customer=self, status='delivered')
        return sum(order.total_amount for order in orders)
