from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from customers.models import Customer
from customers.forms.customer_forms import CustomerForm, CustomerSearchForm


class CustomerListView(LoginRequiredMixin, ListView):
    """
    Liste des clients avec recherche et pagination
    """
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'page_obj'
    paginate_by = 20
    login_url = reverse_lazy('users:login')
    
    def get_queryset(self):
        queryset = Customer.objects.all()
        
        # Récupération des paramètres de recherche
        search_form = CustomerSearchForm(self.request.GET)
        if search_form.is_valid():
            search_type = search_form.cleaned_data.get('search_type')
            search_query = search_form.cleaned_data.get('search_query')
            customer_type = search_form.cleaned_data.get('customer_type')
            is_active = search_form.cleaned_data.get('is_active')
            
            # Application des filtres
            if search_query:
                if search_type == 'name':
                    queryset = queryset.filter(
                        Q(first_name__icontains=search_query) |
                        Q(last_name__icontains=search_query)
                    )
                elif search_type == 'email':
                    queryset = queryset.filter(email__icontains=search_query)
                elif search_type == 'phone':
                    queryset = queryset.filter(phone__icontains=search_query)
                elif search_type == 'company':
                    queryset = queryset.filter(company_name__icontains=search_query)
                elif search_type == 'city':
                    queryset = queryset.filter(city__icontains=search_query)
            
            if customer_type:
                queryset = queryset.filter(customer_type=customer_type)
            
            if is_active:
                queryset = queryset.filter(is_active=is_active == 'True')
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_form = CustomerSearchForm(self.request.GET)
        customers = self.get_queryset()
        
        context.update({
            'search_form': search_form,
            'total_customers': customers.count(),
            'active_customers': customers.filter(is_active=True).count(),
            'company_customers': customers.filter(customer_type='company').count(),
            'individual_customers': customers.filter(customer_type='individual').count(),
        })
        
        return context


class CustomerDetailView(LoginRequiredMixin, DetailView):
    """
    Détail d'un client
    """
    model = Customer
    template_name = 'customers/customer_detail.html'
    context_object_name = 'customer'
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.get_object()
        
        # Récupération des commandes du client
        orders = customer.orders.all().order_by('-order_date')[:10] if hasattr(customer, 'orders') else []
        
        # Récupération des factures du client
        invoices = customer.invoices.all().order_by('-invoice_date')[:10] if hasattr(customer, 'invoices') else []
        
        # Récupération des paiements du client
        payments = customer.payments.all().order_by('-payment_date')[:10] if hasattr(customer, 'payments') else []
        
        context.update({
            'orders': orders,
            'invoices': invoices,
            'payments': payments,
            'total_orders': customer.get_total_orders(),
            'total_spent': customer.get_total_spent(),
        })
        
        return context


class CustomerCreateView(LoginRequiredMixin, CreateView):
    """
    Création d'un nouveau client
    """
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Nouveau client',
            'submit_text': 'Créer le client'
        })
        return context
    
    def get_success_url(self):
        return reverse('customers:customer_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Client "{self.object.full_name}" créé avec succès.')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erreur lors de la création du client. Veuillez corriger les erreurs.')
        return super().form_invalid(form)


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    """
    Modification d'un client existant
    """
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.get_object()
        context.update({
            'title': f'Modifier {customer.full_name}',
            'submit_text': 'Enregistrer les modifications',
            'customer': customer
        })
        return context
    
    def get_success_url(self):
        return reverse('customers:customer_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Client "{self.object.full_name}" modifié avec succès.')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erreur lors de la modification du client. Veuillez corriger les erreurs.')
        return super().form_invalid(form)


class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    """
    Suppression d'un client
    """
    model = Customer
    template_name = 'customers/customer_confirm_delete.html'
    success_url = reverse_lazy('customers:customer_list')
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.get_object()
        
        # Vérification des dépendances
        has_orders = hasattr(customer, 'orders') and customer.orders.exists()
        has_invoices = hasattr(customer, 'invoices') and customer.invoices.exists()
        has_payments = hasattr(customer, 'payments') and customer.payments.exists()
        
        context.update({
            'has_orders': has_orders,
            'has_invoices': has_invoices,
            'has_payments': has_payments,
            'can_delete': not (has_orders or has_invoices or has_payments)
        })
        
        return context
    
    def delete(self, request, *args, **kwargs):
        customer = self.get_object()
        customer_name = customer.full_name
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Client "{customer_name}" supprimé avec succès.')
        return response


class CustomerToggleStatusView(LoginRequiredMixin, View):
    """
    Activation/désactivation d'un client
    """
    login_url = reverse_lazy('users:login')
    
    def post(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        customer.is_active = not customer.is_active
        customer.save()
        
        status = "activé" if customer.is_active else "désactivé"
        messages.success(request, f'Client "{customer.full_name}" {status} avec succès.')
        
        return JsonResponse({
            'success': True,
            'is_active': customer.is_active,
            'message': f'Client {status} avec succès.'
        })
    
    def get(self, request, pk):
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'})


class CustomerQuickSearchView(LoginRequiredMixin, View):
    """
    Recherche rapide de clients pour les formulaires
    """
    login_url = reverse_lazy('users:login')
    
    def get(self, request):
        query = request.GET.get('q', '')
        if len(query) < 2:
            return JsonResponse({'results': []})
        
        customers = Customer.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(company_name__icontains=query) |
            Q(email__icontains=query)
        ).filter(is_active=True)[:10]
        
        results = []
        for customer in customers:
            results.append({
                'id': customer.id,
                'text': customer.display_name,
                'email': customer.email,
                'phone': customer.phone or '',
                'address': customer.full_address
            })
        
        return JsonResponse({'results': results})