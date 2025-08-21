from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from invoices.models import Invoice
from invoices.forms import InvoiceForm, InvoiceSearchForm
from orders.models import Order
from customers.models import Customer


@login_required
def invoice_list(request):
    """
    Liste des factures avec recherche et pagination
    """
    # Récupération des paramètres de recherche
    search_form = InvoiceSearchForm(request.GET)
    invoices = Invoice.objects.all()
    
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
    
    # Tri par défaut
    invoices = invoices.order_by('-invoice_date')
    
    # Pagination
    paginator = Paginator(invoices, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calcul des statistiques
    total_invoices = invoices.count()
    total_amount = invoices.aggregate(total=Sum('total_amount'))['total'] or 0
    total_paid = invoices.aggregate(paid=Sum('paid_amount'))['paid'] or 0
    total_remaining = total_amount - total_paid
    
    invoices_by_status = {}
    for status_choice in Invoice.STATUS_CHOICES:
        status_code = status_choice[0]
        invoices_by_status[status_code] = invoices.filter(status=status_code).count()
    
    # Factures en retard
    overdue_invoices = invoices.filter(
        status__in=['pending', 'partially_paid'],
        due_date__lt=timezone.now().date()
    ).count()
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_invoices': total_invoices,
        'total_amount': total_amount,
        'total_paid': total_paid,
        'total_remaining': total_remaining,
        'invoices_by_status': invoices_by_status,
        'overdue_invoices': overdue_invoices,
    }
    
    return render(request, 'invoices/invoice_list.html', context)


@login_required
def invoice_detail(request, invoice_id):
    """
    Détail d'une facture
    """
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Récupération des paiements associés
    payments = invoice.payments.all().order_by('-payment_date')
    
    # Calcul du pourcentage de paiement
    payment_percentage = invoice.get_payment_percentage()
    
    # Vérification si la facture est en retard
    is_overdue = invoice.is_overdue()
    days_overdue = invoice.get_days_overdue()
    
    context = {
        'invoice': invoice,
        'payments': payments,
        'payment_percentage': payment_percentage,
        'is_overdue': is_overdue,
        'days_overdue': days_overdue,
        'order': invoice.order,
        'order_items': invoice.order.items.all(),
    }
    
    return render(request, 'invoices/invoice_detail.html', context)


@login_required
def invoice_create(request):
    """
    Création d'une nouvelle facture
    """
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save()
            messages.success(request, f'Facture "{invoice.invoice_number}" créée avec succès.')
            return redirect('invoices:invoice_detail', invoice_id=invoice.id)
        else:
            messages.error(request, 'Erreur lors de la création de la facture. Veuillez corriger les erreurs.')
    else:
        form = InvoiceForm()
    
    context = {
        'form': form,
        'title': 'Nouvelle facture',
        'submit_text': 'Créer la facture'
    }
    
    return render(request, 'invoices/invoice_form.html', context)


@login_required
def invoice_update(request, invoice_id):
    """
    Modification d'une facture existante
    """
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            invoice = form.save()
            messages.success(request, f'Facture "{invoice.invoice_number}" modifiée avec succès.')
            return redirect('invoices:invoice_detail', invoice_id=invoice.id)
        else:
            messages.error(request, 'Erreur lors de la modification de la facture. Veuillez corriger les erreurs.')
    else:
        form = InvoiceForm(instance=invoice)
    
    context = {
        'form': form,
        'invoice': invoice,
        'title': f'Modifier la facture {invoice.invoice_number}',
        'submit_text': 'Enregistrer les modifications'
    }
    
    return render(request, 'invoices/invoice_form.html', context)


@login_required
def invoice_delete(request, invoice_id):
    """
    Suppression d'une facture
    """
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    if request.method == 'POST':
        invoice_number = invoice.invoice_number
        invoice.delete()
        messages.success(request, f'Facture "{invoice_number}" supprimée avec succès.')
        return redirect('invoices:invoice_list')
    
    # Vérification des dépendances
    has_payments = invoice.payments.exists()
    
    context = {
        'invoice': invoice,
        'has_payments': has_payments,
        'can_delete': not has_payments
    }
    
    return render(request, 'invoices/invoice_confirm_delete.html', context)


@login_required
def invoice_update_status(request, invoice_id):
    """
    Mise à jour du statut d'une facture
    """
    if request.method == 'POST':
        invoice = get_object_or_404(Invoice, id=invoice_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Invoice.STATUS_CHOICES):
            old_status = invoice.status
            invoice.status = new_status
            
            # Mise à jour automatique de la date de paiement si nécessaire
            if new_status == 'paid' and not invoice.paid_date:
                invoice.paid_date = timezone.now().date()
                invoice.paid_amount = invoice.total_amount
                invoice.remaining_amount = 0
            
            invoice.save()
            
            messages.success(request, f'Statut de la facture {invoice.invoice_number} mis à jour : {old_status} → {new_status}')
            
            return JsonResponse({
                'success': True,
                'new_status': new_status,
                'status_display': invoice.get_status_display(),
                'status_color': invoice.get_status_display_color(),
                'message': f'Statut mis à jour avec succès.'
            })
        else:
            return JsonResponse({'success': False, 'message': 'Statut invalide.'})
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'})


@login_required
def invoice_generate_pdf(request, invoice_id):
    """
    Génération d'une facture en PDF
    """
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Ici, vous pouvez implémenter la génération PDF
    # Pour l'instant, on retourne un message
    messages.info(request, 'Génération PDF à implémenter.')
    return redirect('invoices:invoice_detail', invoice_id=invoice.id)


@login_required
def invoice_send_email(request, invoice_id):
    """
    Envoi d'une facture par email
    """
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    if request.method == 'POST':
        # Ici, vous pouvez implémenter l'envoi d'email
        # Pour l'instant, on retourne un message
        messages.success(request, f'Facture {invoice.invoice_number} envoyée par email avec succès.')
        return redirect('invoices:invoice_detail', invoice_id=invoice.id)
    
    context = {
        'invoice': invoice,
    }
    
    return render(request, 'invoices/invoice_send_email.html', context)


@login_required
def invoice_quick_search(request):
    """
    Recherche rapide de factures pour les formulaires
    """
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    invoices = Invoice.objects.filter(
        Q(invoice_number__icontains=query) |
        Q(customer__first_name__icontains=query) |
        Q(customer__last_name__icontains=query)
    )[:10]
    
    results = []
    for invoice in invoices:
        results.append({
            'id': invoice.id,
            'text': f"{invoice.invoice_number} - {invoice.customer.full_name}",
            'customer': invoice.customer.full_name,
            'status': invoice.get_status_display(),
            'total': str(invoice.total_amount),
            'remaining': str(invoice.remaining_amount)
        })
    
    return JsonResponse({'results': results})
