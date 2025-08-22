/**
 * COMMANDLY DESIGN SYSTEM - JavaScript centralisé
 * Gestion des interactions, animations et comportements UI
 * Basé sur les guidelines design-guidelines.md
 */

class CommandlyDesignSystem {
  constructor() {
    this.init();
  }

  /**
   * Initialisation du système
   */
  init() {
    this.setupEventListeners();
    this.initAnimations();
    this.initTooltips();
    this.initModals();
    this.initForms();
    this.initSidebar();
  }

  /**
   * Configuration des écouteurs d'événements
   */
  setupEventListeners() {
    document.addEventListener('DOMContentLoaded', () => {
      this.handlePageLoad();
    });

    // Gestion des clics sur les boutons
    document.addEventListener('click', (e) => {
      if (e.target.matches('.btn') || e.target.closest('.btn')) {
        this.handleButtonClick(e);
      }
      
      // Gestion du menu mobile
      if (e.target.matches('.sidebar-toggle')) {
        this.toggleSidebar();
      }
    });

    // Gestion des formulaires
    document.addEventListener('submit', (e) => {
      if (e.target.matches('form')) {
        this.handleFormSubmit(e);
      }
    });

    // Gestion du redimensionnement
    window.addEventListener('resize', this.debounce(() => {
      this.handleResize();
    }, 250));
  }

  /**
   * Gestion du chargement de page
   */
  handlePageLoad() {
    // Animation d'entrée des éléments
    this.animateElements();
    
    // Mise à jour des états actifs dans la navigation
    this.updateActiveNavigation();
    
    // Initialisation des composants spéciaux
    this.initSpecialComponents();
  }

  /**
   * Animation des éléments au chargement
   */
  animateElements() {
    const animatedElements = document.querySelectorAll('.card, .kpi-card');
    
    animatedElements.forEach((element, index) => {
      element.style.opacity = '0';
      element.style.transform = 'translateY(20px)';
      
      setTimeout(() => {
        element.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
      }, index * 100);
    });
  }

  /**
   * Mise à jour de la navigation active
   */
  updateActiveNavigation() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
      const href = link.getAttribute('href');
      if (href && currentPath.startsWith(href) && href !== '/') {
        link.classList.add('active');
      } else if (href === '/' && currentPath === '/') {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  }

  /**
   * Gestion des clics sur les boutons
   */
  handleButtonClick(e) {
    const button = e.target.matches('.btn') ? e.target : e.target.closest('.btn');
    
    // Effet de clic
    if (!button.disabled) {
      button.style.transform = 'scale(0.98)';
      setTimeout(() => {
        button.style.transform = '';
      }, 150);
    }

    // Gestion des boutons de suppression
    if (button.classList.contains('btn-danger') && button.dataset.confirm) {
      e.preventDefault();
      this.showConfirmDialog(button.dataset.confirm, () => {
        if (button.href) {
          window.location.href = button.href;
        } else if (button.form) {
          button.form.submit();
        }
      });
    }
  }

  /**
   * Gestion des formulaires
   */
  initForms() {
    // Validation en temps réel
    const inputs = document.querySelectorAll('.form-control');
    
    inputs.forEach(input => {
      input.addEventListener('blur', () => {
        this.validateField(input);
      });
      
      input.addEventListener('input', () => {
        if (input.classList.contains('is-invalid')) {
          this.validateField(input);
        }
      });
    });
  }

  /**
   * Validation d'un champ de formulaire
   */
  validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';

    // Validation des champs requis
    if (field.required && !value) {
      isValid = false;
      errorMessage = 'Ce champ est requis';
    }

    // Validation des emails
    if (field.type === 'email' && value) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(value)) {
        isValid = false;
        errorMessage = 'Format d\'email invalide';
      }
    }

    // Validation des téléphones (Sénégal)
    if (field.name === 'phone' && value) {
      const phoneRegex = /^\+221[0-9]{9}$/;
      if (!phoneRegex.test(value)) {
        isValid = false;
        errorMessage = 'Format: +221XXXXXXXXX';
      }
    }

    // Mise à jour de l'interface
    this.updateFieldValidation(field, isValid, errorMessage);
    
    return isValid;
  }

  /**
   * Mise à jour de l'affichage de validation
   */
  updateFieldValidation(field, isValid, errorMessage) {
    field.classList.remove('is-valid', 'is-invalid');
    
    // Suppression des anciens messages d'erreur
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
      existingError.remove();
    }

    if (isValid) {
      field.classList.add('is-valid');
    } else {
      field.classList.add('is-invalid');
      
      // Ajout du message d'erreur
      const errorDiv = document.createElement('div');
      errorDiv.className = 'invalid-feedback';
      errorDiv.textContent = errorMessage;
      field.parentNode.appendChild(errorDiv);
    }
  }

  /**
   * Gestion de la soumission de formulaire
   */
  handleFormSubmit(e) {
    const form = e.target;
    const inputs = form.querySelectorAll('.form-control[required]');
    let isFormValid = true;

    inputs.forEach(input => {
      if (!this.validateField(input)) {
        isFormValid = false;
      }
    });

    if (!isFormValid) {
      e.preventDefault();
      this.showNotification('Veuillez corriger les erreurs du formulaire', 'error');
    } else {
      // Affichage du loader sur le bouton de soumission
      const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
      if (submitBtn) {
        this.showButtonLoading(submitBtn);
      }
    }
  }

  /**
   * Affichage du loader sur un bouton
   */
  showButtonLoading(button) {
    const originalText = button.textContent;
    const originalHTML = button.innerHTML;
    
    button.disabled = true;
    button.innerHTML = '<i class="bi bi-arrow-clockwise spinner"></i> Chargement...';
    
    // Restauration après 5 secondes (sécurité)
    setTimeout(() => {
      button.disabled = false;
      button.innerHTML = originalHTML;
    }, 5000);
  }

  /**
   * Initialisation de la sidebar
   */
  initSidebar() {
    // Gestion du toggle mobile
    const toggleBtn = document.querySelector('.sidebar-toggle');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => {
        this.toggleSidebar();
      });
    }

    // Fermeture automatique en mobile lors du clic sur un lien
    if (window.innerWidth <= 640) {
      document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
          this.closeSidebar();
        });
      });
    }
  }

  /**
   * Toggle de la sidebar
   */
  toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
      sidebar.classList.toggle('open');
    }
  }

  /**
   * Fermeture de la sidebar
   */
  closeSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
      sidebar.classList.remove('open');
    }
  }

  /**
   * Gestion du redimensionnement
   */
  handleResize() {
    // Fermeture automatique de la sidebar en desktop
    if (window.innerWidth > 640) {
      this.closeSidebar();
    }
  }

  /**
   * Initialisation des tooltips
   */
  initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
      element.addEventListener('mouseenter', (e) => {
        this.showTooltip(e.target);
      });
      
      element.addEventListener('mouseleave', (e) => {
        this.hideTooltip(e.target);
      });
    });
  }

  /**
   * Affichage d'un tooltip
   */
  showTooltip(element) {
    const text = element.dataset.tooltip;
    if (!text) return;

    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    tooltip.style.cssText = `
      position: absolute;
      background: #333;
      color: white;
      padding: 8px 12px;
      border-radius: 6px;
      font-size: 14px;
      z-index: 1000;
      white-space: nowrap;
      pointer-events: none;
    `;

    document.body.appendChild(tooltip);

    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';

    element._tooltip = tooltip;
  }

  /**
   * Masquage d'un tooltip
   */
  hideTooltip(element) {
    if (element._tooltip) {
      element._tooltip.remove();
      delete element._tooltip;
    }
  }

  /**
   * Initialisation des modales
   */
  initModals() {
    // Fermeture des modales avec Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.closeAllModals();
      }
    });
  }

  /**
   * Fermeture de toutes les modales
   */
  closeAllModals() {
    const modals = document.querySelectorAll('.modal.show');
    modals.forEach(modal => {
      // Si Bootstrap modal
      if (window.bootstrap && bootstrap.Modal) {
        const modalInstance = bootstrap.Modal.getInstance(modal);
        if (modalInstance) {
          modalInstance.hide();
        }
      }
    });
  }

  /**
   * Affichage d'une boîte de dialogue de confirmation
   */
  showConfirmDialog(message, onConfirm, onCancel = null) {
    const confirmed = confirm(message);
    if (confirmed && onConfirm) {
      onConfirm();
    } else if (!confirmed && onCancel) {
      onCancel();
    }
  }

  /**
   * Affichage d'une notification
   */
  showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
      <div class="notification-content">
        <i class="bi bi-${this.getNotificationIcon(type)}"></i>
        <span>${message}</span>
        <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
          <i class="bi bi-x"></i>
        </button>
      </div>
    `;

    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: white;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      padding: 16px;
      z-index: 1050;
      min-width: 300px;
      animation: slideInRight 0.3s ease-out;
    `;

    // Couleurs selon le type
    const colors = {
      success: '#16A34A',
      error: '#DC2626',
      warning: '#F97316',
      info: '#2D6EEA'
    };

    notification.style.borderLeft = `4px solid ${colors[type] || colors.info}`;

    document.body.appendChild(notification);

    // Suppression automatique
    setTimeout(() => {
      if (notification.parentNode) {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => {
          notification.remove();
        }, 300);
      }
    }, duration);
  }

  /**
   * Icône pour les notifications
   */
  getNotificationIcon(type) {
    const icons = {
      success: 'check-circle',
      error: 'exclamation-circle',
      warning: 'exclamation-triangle',
      info: 'info-circle'
    };
    return icons[type] || icons.info;
  }

  /**
   * Initialisation des composants spéciaux
   */
  initSpecialComponents() {
    // Animation des KPI cards au survol
    document.querySelectorAll('.kpi-card').forEach(card => {
      card.addEventListener('mouseenter', () => {
        card.style.transform = 'translateY(-4px) scale(1.02)';
      });
      
      card.addEventListener('mouseleave', () => {
        card.style.transform = '';
      });
    });

    // Gestion des tableaux
    this.initTables();
  }

  /**
   * Initialisation des tableaux
   */
  initTables() {
    const tables = document.querySelectorAll('.table');
    
    tables.forEach(table => {
      // Ajout de classes pour le style
      table.classList.add('table-hover');
      
      // Gestion de la sélection de lignes
      const rows = table.querySelectorAll('tbody tr');
      rows.forEach(row => {
        row.addEventListener('click', (e) => {
          // Ne pas sélectionner si on clique sur un bouton ou lien
          if (!e.target.matches('a, button, .btn, input')) {
            row.classList.toggle('selected');
          }
        });
      });
    });
  }

  /**
   * Utilitaire de debounce
   */
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
}

// Ajout des styles CSS pour les animations
const style = document.createElement('style');
style.textContent = `
  @keyframes slideInRight {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  
  @keyframes slideOutRight {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
  }
  
  .spinner {
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  .notification-content {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  
  .notification-close {
    background: none;
    border: none;
    cursor: pointer;
    opacity: 0.7;
    margin-left: auto;
  }
  
  .notification-close:hover {
    opacity: 1;
  }
  
  .table tbody tr.selected {
    background-color: var(--color-primary-light, #E0E7FF);
  }
`;
document.head.appendChild(style);

// Initialisation automatique
const designSystem = new CommandlyDesignSystem();

// Export pour utilisation externe
window.CommandlyDesignSystem = CommandlyDesignSystem;
window.designSystem = designSystem;
