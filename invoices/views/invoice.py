from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.views import View as BaseView
from invoices.models import Invoice
from invoices.forms.invoice_forms import InvoiceForm, InvoiceSearchForm
from orders.models import Order
from customers.models import Customer


class InvoiceListView(LoginRequiredMixin, ListView):
    """
    Liste des factures avec recherche et pagination
    """
    model = Invoice
    template_name = 'invoices/invoice_list.html'
    context_object_name = 'page_obj'
    paginate_by = 20
    login_url = reverse_lazy('users:login')
    
    def get_queryset(self):
        invoices = Invoice.objects.all()
        
        # Récupération des paramètres de recherche
        search_form = InvoiceSearchForm(self.request.GET)
        if search_form.is_valid():
            search_type = search_form.cleaned_data.get('search_type')
            search_query = search_form.cleaned_data.get('search_query')
            customer = search_form.cleaned_data.get('customer')
            status = search_form.cleaned_data.get('status')
            date_from = search_form.cleaned_data.get('date_from')
            date_to = search_form.cleaned_data.get('date_to')
            due_date_from = search_form.cleaned_data.get('due_date_from')
            due_date_to = search_form.cleaned_data.get('due_date_to')
            amount_min = search_form.cleaned_data.get('amount_min')
            amount_max = search_form.cleaned_data.get('amount_max')
            payment_status = search_form.cleaned_data.get('payment_status')
            
            # Application des filtres
            if search_query:
                if search_type == 'invoice_number':
                    invoices = invoices.filter(invoice_number__icontains=search_query)
                elif search_type == 'customer':
                    invoices = invoices.filter(
                        Q(customer__first_name__icontains=search_query) |
                        Q(customer__last_name__icontains=search_query) |
                        Q(customer__company_name__icontains=search_query)
                    )
                elif search_type == 'status':
                    invoices = invoices.filter(status__icontains=search_query)
                elif search_type == 'date':
                    invoices = invoices.filter(invoice_date__date__icontains=search_query)
                elif search_type == 'amount':
                    invoices = invoices.filter(total_amount__icontains=search_query)
            
            if customer:
                invoices = invoices.filter(customer=customer)
            
            if status:
                invoices = invoices.filter(status=status)
            
            if date_from:
                invoices = invoices.filter(invoice_date__date__gte=date_from)
            
            if date_to:
                invoices = invoices.filter(invoice_date__date__lte=date_to)
            
            if due_date_from:
                invoices = invoices.filter(due_date__gte=due_date_from)
            
            if due_date_to:
                invoices = invoices.filter(due_date__lte=due_date_to)
            
            if amount_min:
                invoices = invoices.filter(total_amount__gte=amount_min)
            
            if amount_max:
                invoices = invoices.filter(total_amount__lte=amount_max)
            
            if payment_status:
                if payment_status == 'paid':
                    invoices = invoices.filter(status='paid')
                elif payment_status == 'partially_paid':
                    invoices = invoices.filter(status='partially_paid')
                elif payment_status == 'pending':
                    invoices = invoices.filter(status='pending')
                elif payment_status == 'overdue':
                    invoices = invoices.filter(status='overdue')
        
        return invoices.order_by('-invoice_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_form = InvoiceSearchForm(self.request.GET)
        invoices = self.get_queryset()
        
        # Calcul des statistiques
        total_invoices = invoices.count()
        total_amount = invoices.aggregate(total=Sum('total_amount'))['total'] or 0
        total_paid = invoices.aggregate(paid=Sum('paid_amount'))['paid'] or 0
        total_remaining = total_amount - total_paid
        
        invoices_by_status = {}
        for status_choice in Invoice.STATUS_CHOICES:
            status_code = status_choice[0]
            invoices_by_status[status_code] = invoices.filter(status=status_code).count()
        
        context.update({
            'search_form': search_form,
            'total_invoices': total_invoices,
            'total_amount': total_amount,
            'total_paid': total_paid,
            'total_remaining': total_remaining,
            'invoices_by_status': invoices_by_status,
        })
        
        return context


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    """
    Détail d'une facture
    """
    model = Invoice
    template_name = 'invoices/invoice_detail.html'
    context_object_name = 'invoice'
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice = self.get_object()
        
        # Récupération des paiements associés
        payments = invoice.payments.all().order_by('-payment_date')
        
        context.update({
            'payments': payments,
            'subtotal_ht': invoice.subtotal_ht,
            'tax_amount': invoice.tax_amount,
            'total_amount': invoice.total_amount,
            'paid_amount': invoice.paid_amount,
            'remaining_amount': invoice.remaining_amount,
        })
        
        return context


class InvoiceCreateView(LoginRequiredMixin, CreateView):
    """
    Création d'une nouvelle facture
    """
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoices/invoice_form.html'
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Nouvelle facture',
            'submit_text': 'Créer la facture'
        })
        return context
    
    def form_valid(self, form):
        invoice = form.save()
        messages.success(self.request, f'Facture "{invoice.invoice_number}" créée avec succès.')
        return redirect('invoices:invoice_detail', pk=invoice.pk)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erreur lors de la création de la facture. Veuillez corriger les erreurs.')
        return super().form_invalid(form)


class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    """
    Modification d'une facture existante
    """
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoices/invoice_form.html'
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice = self.get_object()
        context.update({
            'title': f'Modifier la facture {invoice.invoice_number}',
            'submit_text': 'Enregistrer les modifications',
            'invoice': invoice
        })
        return context
    
    def form_valid(self, form):
        invoice = form.save()
        messages.success(self.request, f'Facture "{invoice.invoice_number}" modifiée avec succès.')
        return redirect('invoices:invoice_detail', pk=invoice.pk)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erreur lors de la modification de la facture. Veuillez corriger les erreurs.')
        return super().form_invalid(form)


class InvoiceDeleteView(LoginRequiredMixin, DeleteView):
    """
    Suppression d'une facture
    """
    model = Invoice
    template_name = 'invoices/invoice_confirm_delete.html'
    success_url = reverse_lazy('invoices:invoice_list')
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice = self.get_object()
        
        # Vérification des dépendances
        has_payments = invoice.payments.exists()
        
        context.update({
            'has_payments': has_payments,
            'can_delete': not has_payments
        })
        
        return context
    
    def delete(self, request, *args, **kwargs):
        invoice = self.get_object()
        invoice_number = invoice.invoice_number
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Facture "{invoice_number}" supprimée avec succès.')
        return response


class InvoicePDFView(LoginRequiredMixin, BaseView):
    """
    Génération du PDF d'une facture
    """
    login_url = reverse_lazy('users:login')
    
    def get(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        
        # Ici nous générerions le PDF de la facture
        # Pour l'instant, nous retournons une réponse simple
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="facture_{invoice.invoice_number}.pdf"'
        
        # TODO: Implémenter la génération PDF
        response.write(b'PDF content would go here')
        
        return response


class InvoiceStatusUpdateView(LoginRequiredMixin, BaseView):
    """
    Mise à jour du statut d'une facture
    """
    login_url = reverse_lazy('users:login')
    
    def post(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in dict(Invoice.STATUS_CHOICES):
            old_status = invoice.status
            invoice.status = new_status
            invoice.save()
            
            messages.success(request, f'Statut de la facture {invoice.invoice_number} mis à jour : {old_status} → {new_status}')
            
            return JsonResponse({
                'success': True,
                'new_status': new_status,
                'status_display': invoice.get_status_display(),
                'message': f'Statut mis à jour avec succès.'
            })
        else:
            return JsonResponse({'success': False, 'message': 'Statut invalide.'})
    
    def get(self, request, pk):
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'})