from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from payments.models import Payment
from payments.forms.payment_forms import PaymentForm, PaymentSearchForm
from invoices.models import Invoice
from customers.models import Customer


class PaymentListView(LoginRequiredMixin, ListView):
    """
    Liste des paiements avec recherche et pagination
    """
    model = Payment
    template_name = 'payments/payment_list.html'
    context_object_name = 'page_obj'
    paginate_by = 20
    login_url = reverse_lazy('users:login')
    
    def get_queryset(self):
        payments = Payment.objects.all()
        
        # Récupération des paramètres de recherche
        search_form = PaymentSearchForm(self.request.GET)
        if search_form.is_valid():
            search_type = search_form.cleaned_data.get('search_type')
            search_query = search_form.cleaned_data.get('search_query')
            customer = search_form.cleaned_data.get('customer')
            invoice = search_form.cleaned_data.get('invoice')
            payment_method = search_form.cleaned_data.get('payment_method')
            date_from = search_form.cleaned_data.get('date_from')
            date_to = search_form.cleaned_data.get('date_to')
            amount_min = search_form.cleaned_data.get('amount_min')
            amount_max = search_form.cleaned_data.get('amount_max')
            
            # Application des filtres
            if search_query:
                if search_type == 'reference':
                    payments = payments.filter(reference__icontains=search_query)
                elif search_type == 'customer':
                    payments = payments.filter(
                        Q(customer__first_name__icontains=search_query) |
                        Q(customer__last_name__icontains=search_query) |
                        Q(customer__company_name__icontains=search_query)
                    )
                elif search_type == 'invoice':
                    payments = payments.filter(invoice__invoice_number__icontains=search_query)
                elif search_type == 'amount':
                    payments = payments.filter(amount__icontains=search_query)
            
            if customer:
                payments = payments.filter(customer=customer)
            
            if invoice:
                payments = payments.filter(invoice=invoice)
            
            if payment_method:
                payments = payments.filter(payment_method=payment_method)
            
            if date_from:
                payments = payments.filter(payment_date__gte=date_from)
            
            if date_to:
                payments = payments.filter(payment_date__lte=date_to)
            
            if amount_min:
                payments = payments.filter(amount__gte=amount_min)
            
            if amount_max:
                payments = payments.filter(amount__lte=amount_max)
        
        return payments.order_by('-payment_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_form = PaymentSearchForm(self.request.GET)
        payments = self.get_queryset()
        
        # Calcul des statistiques
        total_payments = payments.count()
        total_amount = payments.aggregate(total=Sum('amount'))['total'] or 0
        
        payments_by_method = {}
        for method_choice in Payment.PAYMENT_METHOD_CHOICES:
            method_code = method_choice[0]
            payments_by_method[method_code] = payments.filter(payment_method=method_code).count()
        
        context.update({
            'search_form': search_form,
            'total_payments': total_payments,
            'total_amount': total_amount,
            'payments_by_method': payments_by_method,
        })
        
        return context


class PaymentDetailView(LoginRequiredMixin, DetailView):
    """
    Détail d'un paiement
    """
    model = Payment
    template_name = 'payments/payment_detail.html'
    context_object_name = 'payment'
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment = self.get_object()
        
        context.update({
            'invoice': payment.invoice,
            'customer': payment.customer,
        })
        
        return context


class PaymentCreateView(LoginRequiredMixin, CreateView):
    """
    Création d'un nouveau paiement
    """
    model = Payment
    form_class = PaymentForm
    template_name = 'payments/payment_form.html'
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Nouveau paiement',
            'submit_text': 'Enregistrer le paiement'
        })
        return context
    
    def get_success_url(self):
        return reverse('payments:payment_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Paiement "{self.object.reference}" créé avec succès.')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erreur lors de la création du paiement. Veuillez corriger les erreurs.')
        return super().form_invalid(form)


class PaymentUpdateView(LoginRequiredMixin, UpdateView):
    """
    Modification d'un paiement existant
    """
    model = Payment
    form_class = PaymentForm
    template_name = 'payments/payment_form.html'
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment = self.get_object()
        context.update({
            'title': f'Modifier le paiement {payment.reference}',
            'submit_text': 'Enregistrer les modifications',
            'payment': payment
        })
        return context
    
    def get_success_url(self):
        return reverse('payments:payment_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Paiement "{self.object.reference}" modifié avec succès.')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erreur lors de la modification du paiement. Veuillez corriger les erreurs.')
        return super().form_invalid(form)


class PaymentDeleteView(LoginRequiredMixin, DeleteView):
    """
    Suppression d'un paiement
    """
    model = Payment
    template_name = 'payments/payment_confirm_delete.html'
    success_url = reverse_lazy('payments:payment_list')
    login_url = reverse_lazy('users:login')
    
    def delete(self, request, *args, **kwargs):
        payment = self.get_object()
        payment_reference = payment.reference
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Paiement "{payment_reference}" supprimé avec succès.')
        return response