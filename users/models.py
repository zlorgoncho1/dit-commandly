from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):
    """
    Modèle utilisateur personnalisé étendant AbstractUser
    Gère les rôles Admin, Vendeur et Client
    """
    
    # Rôles disponibles
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('seller', 'Vendeur'),
        ('client', 'Client'),
    ]
    
    # Champs personnalisés
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='client',
        verbose_name='Rôle'
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
    
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name='Adresse'
    )
    
    company_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Nom de l\'entreprise'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Compte actif'
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
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['-date_joined']
    
    def __str__(self):
        if self.company_name:
            return f"{self.company_name} - {self.get_full_name()}"
        return self.get_full_name() or self.username
    
    @property
    def is_admin(self):
        """Vérifie si l'utilisateur est administrateur"""
        return self.role == 'admin'
    
    @property
    def is_seller(self):
        """Vérifie si l'utilisateur est vendeur"""
        return self.role == 'seller'
    
    @property
    def is_client(self):
        """Vérifie si l'utilisateur est client"""
        return self.role == 'client'
    
    def can_manage_orders(self):
        """Vérifie si l'utilisateur peut gérer les commandes"""
        return self.role in ['admin', 'seller']
    
    def can_manage_products(self):
        """Vérifie si l'utilisateur peut gérer les produits"""
        return self.role in ['admin', 'seller']
    
    def can_manage_users(self):
        """Vérifie si l'utilisateur peut gérer les utilisateurs"""
        return self.role == 'admin'
