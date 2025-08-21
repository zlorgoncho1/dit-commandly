from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.utils import timezone
from payments.models import Payment
from payments.forms import PaymentForm, PaymentSearchForm
from invoices.models import Invoice
from customers.models import Customer


@login_required
def payment_list(request):
    """
    Liste des paiements avec recherche et pagination
    """
    # Récupération des paramètres de recherche
    search_form = PaymentSearchForm(request.GET)
    payments = Payment.objects.all()
    
    if search_form.is_valid():
        search_type = search_form.cleaned_data.get('search_type')
        search_query = search_form.cleaned_data.get('search_query')
        customer = search_form.cleaned_data.get('customer')
        invoice = search_form.cleaned_data.get('invoice')
        status = search_form.cleaned_data.get('status')
        payment_method = search_form.cleaned_data.get('payment_method')
        date_from = search_form.cleaned_data.get('date_from')
        date_to = search_form.cleaned_data.get('date_to')
        amount_min = search_form.cleaned_data.get('amount_min')
        amount_max = search_form.cleaned_data.get('amount_max')
        
        # Application des filtres
        if search_query:
            if search_type == 'payment_number':
                payments = payments.filter(payment_number__icontains=search_query)
            elif search_type == 'customer':
                payments = payments.filter(
                    Q(customer__first_name__icontains=search_query) |
                    Q(customer__last_name__icontains=search_query) |
                    Q(customer__company_name__icontains=search_query)
                )
            elif search_type == 'invoice':
                payments = payments.filter(invoice__invoice_number__icontains=search_query)
            elif search_type == 'status':
                payments = payments.filter(status__icontains=search_query)
            elif search_type == 'method':
                payments = payments.filter(payment_method__icontains=search_query)
            elif search_type == 'date':
                payments = payments.filter(payment_date__date__icontains=search_query)
        
        if customer:
            payments = payments.filter(customer=customer)
        
        if invoice:
            payments = payments.filter(invoice=invoice)
        
        if status:
            payments = payments.filter(status=status)
        
        if payment_method:
            payments = payments.filter(payment_method=payment_method)
        
        if date_from:
            payments = payments.filter(payment_date__date__gte=date_from)
        
        if date_to:
            payments = payments.filter(payment_date__date__lte=date_to)
        
        if amount_min:
            payments = payments.filter(amount__gte=amount_min)
        
        if amount_max:
            payments = payments.filter(amount__lte=amount_max)
    
    # Tri par défaut
    payments = payments.order_by('-payment_date')
    
    # Pagination
    paginator = Paginator(payments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calcul des statistiques
    total_payments = payments.count()
    total_amount = payments.aggregate(total=Sum('amount'))['total'] or 0
    completed_payments = payments.filter(status='completed')
    completed_amount = completed_payments.aggregate(total=Sum('amount'))['total'] or 0
    
    payments_by_status = {}
    for status_choice in Payment.STATUS_CHOICES:
        status_code = status_choice[0]
        payments_by_status[status_code] = payments.filter(status=status_code).count()
    
    payments_by_method = {}
    for method_choice in Payment.PAYMENT_METHOD_CHOICES:
        method_code = method_choice[0]
        payments_by_method[method_code] = payments.filter(payment_method=method_code).count()
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_payments': total_payments,
        'total_amount': total_amount,
        'completed_amount': completed_amount,
        'payments_by_status': payments_by_status,
        'payments_by_method': payments_by_method,
    }
    
    return render(request, 'payments/payment_list.html', context)


@login_required
def payment_detail(request, payment_id):
    """
    Détail d'un paiement
    """
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Récupération des informations de la facture
    invoice = payment.invoice
    
    context = {
        'payment': payment,
        'invoice': invoice,
        'customer': payment.customer,
    }
    
    return render(request, 'payments/payment_detail.html', context)


@login_required
def payment_create(request):
    """
    Création d'un nouveau paiement
    """
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.created_by = request.user
            payment.save()
            
            messages.success(request, f'Paiement "{payment.payment_number}" créé avec succès.')
            return redirect('payments:payment_detail', payment_id=payment.id)
        else:
            messages.error(request, 'Erreur lors de la création du paiement. Veuillez corriger les erreurs.')
    else:
        form = PaymentForm()
    
    context = {
        'form': form,
        'title': 'Nouveau paiement',
        'submit_text': 'Créer le paiement'
    }
    
    return render(request, 'payments/payment_form.html', context)


@login_required
def payment_update(request, payment_id):
    """
    Modification d'un paiement existant
    """
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            payment = form.save()
            messages.success(request, f'Paiement "{payment.payment_number}" modifié avec succès.')
            return redirect('payments:payment_detail', payment_id=payment.id)
        else:
            messages.error(request, 'Erreur lors de la modification du paiement. Veuillez corriger les erreurs.')
    else:
        form = PaymentForm(instance=payment)
    
    context = {
        'form': form,
        'payment': payment,
        'title': f'Modifier le paiement {payment.payment_number}',
        'submit_text': 'Enregistrer les modifications'
    }
    
    return render(request, 'payments/payment_form.html', context)


@login_required
def payment_delete(request, payment_id):
    """
    Suppression d'un paiement
    """
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        payment_number = payment.payment_number
        payment.delete()
        messages.success(request, f'Paiement "{payment_number}" supprimé avec succès.')
        return redirect('payments:payment_list')
    
    context = {
        'payment': payment,
    }
    
    return render(request, 'payments/payment_confirm_delete.html', context)


@login_required
def payment_update_status(request, payment_id):
    """
    Mise à jour du statut d'un paiement
    """
    if request.method == 'POST':
        payment = get_object_or_404(Payment, id=payment_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Payment.STATUS_CHOICES):
            old_status = payment.status
            payment.status = new_status
            
            # Mise à jour automatique de la date de traitement si nécessaire
            if new_status == 'completed' and not payment.processed_date:
                payment.processed_date = timezone.now()
            
            payment.save()
            
            messages.success(request, f'Statut du paiement {payment.payment_number} mis à jour : {old_status} → {new_status}')
            
            return JsonResponse({
                'success': True,
                'new_status': new_status,
                'status_display': payment.get_status_display(),
                'status_color': payment.get_status_display_color(),
                'message': f'Statut mis à jour avec succès.'
            })
        else:
            return JsonResponse({'success': False, 'message': 'Statut invalide.'})
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'})


@login_required
def payment_mark_completed(request, payment_id):
    """
    Marquer un paiement comme complété
    """
    if request.method == 'POST':
        payment = get_object_or_404(Payment, id=payment_id)
        
        if payment.can_be_processed():
            payment.mark_as_completed()
            messages.success(request, f'Paiement "{payment.payment_number}" marqué comme complété.')
            
            return JsonResponse({
                'success': True,
                'status': payment.status,
                'status_display': payment.get_status_display(),
                'status_color': payment.get_status_display_color(),
                'message': 'Paiement marqué comme complété.'
            })
        else:
            return JsonResponse({'success': False, 'message': 'Le paiement ne peut pas être traité.'})
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'})


@login_required
def payment_mark_failed(request, payment_id):
    """
    Marquer un paiement comme échoué
    """
    if request.method == 'POST':
        payment = get_object_or_404(Payment, id=payment_id)
        
        if payment.status == 'pending':
            payment.mark_as_failed()
            messages.warning(request, f'Paiement "{payment.payment_number}" marqué comme échoué.')
            
            return JsonResponse({
                'success': True,
                'status': payment.status,
                'status_display': payment.get_status_display(),
                'status_color': payment.get_status_display_color(),
                'message': 'Paiement marqué comme échoué.'
            })
        else:
            return JsonResponse({'success': False, 'message': 'Le paiement ne peut pas être marqué comme échoué.'})
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'})


@login_required
def payment_mark_cancelled(request, payment_id):
    """
    Marquer un paiement comme annulé
    """
    if request.method == 'POST':
        payment = get_object_or_404(Payment, id=payment_id)
        
        if payment.can_be_cancelled():
            payment.mark_as_cancelled()
            messages.info(request, f'Paiement "{payment.payment_number}" marqué comme annulé.')
            
            return JsonResponse({
                'success': True,
                'status': payment.status,
                'status_display': payment.get_status_display(),
                'status_color': payment.get_status_display_color(),
                'message': 'Paiement marqué comme annulé.'
            })
        else:
            return JsonResponse({'success': False, 'message': 'Le paiement ne peut pas être annulé.'})
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'})


@login_required
def payment_quick_search(request):
    """
    Recherche rapide de paiements pour les formulaires
    """
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    payments = Payment.objects.filter(
        Q(payment_number__icontains=query) |
        Q(customer__first_name__icontains=query) |
        Q(customer__last_name__icontains=query) |
        Q(invoice__invoice_number__icontains=query)
    )[:10]
    
    results = []
    for payment in payments:
        results.append({
            'id': payment.id,
            'text': f"{payment.payment_number} - {payment.customer.full_name}",
            'customer': payment.customer.full_name,
            'invoice': payment.invoice.invoice_number,
            'amount': str(payment.amount),
            'status': payment.get_status_display()
        })
    
    return JsonResponse({'results': results})
