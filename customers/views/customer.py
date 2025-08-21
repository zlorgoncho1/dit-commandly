from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from customers.models import Customer
from customers.forms import CustomerForm, CustomerSearchForm


@login_required
def customer_list(request):
    """
    Liste des clients avec recherche et pagination
    """
    # Récupération des paramètres de recherche
    search_form = CustomerSearchForm(request.GET)
    customers = Customer.objects.all()
    
    if search_form.is_valid():
        search_type = search_form.cleaned_data.get('search_type')
        search_query = search_form.cleaned_data.get('search_query')
        customer_type = search_form.cleaned_data.get('customer_type')
        is_active = search_form.cleaned_data.get('is_active')
        
        # Application des filtres
        if search_query:
            if search_type == 'name':
                customers = customers.filter(
                    Q(first_name__icontains=search_query) |
                    Q(last_name__icontains=search_query)
                )
            elif search_type == 'email':
                customers = customers.filter(email__icontains=search_query)
            elif search_type == 'phone':
                customers = customers.filter(phone__icontains=search_query)
            elif search_type == 'company':
                customers = customers.filter(company_name__icontains=search_query)
            elif search_type == 'city':
                customers = customers.filter(city__icontains=search_query)
        
        if customer_type:
            customers = customers.filter(customer_type=customer_type)
        
        if is_active:
            customers = customers.filter(is_active=is_active == 'True')
    
    # Tri par défaut
    customers = customers.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(customers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_customers': customers.count(),
        'active_customers': customers.filter(is_active=True).count(),
        'company_customers': customers.filter(customer_type='company').count(),
        'individual_customers': customers.filter(customer_type='individual').count(),
    }
    
    return render(request, 'customers/customer_list.html', context)


@login_required
def customer_detail(request, customer_id):
    """
    Détail d'un client
    """
    customer = get_object_or_404(Customer, id=customer_id)
    
    # Récupération des commandes du client
    orders = customer.orders.all().order_by('-order_date')[:10]
    
    # Récupération des factures du client
    invoices = customer.invoices.all().order_by('-invoice_date')[:10]
    
    # Récupération des paiements du client
    payments = customer.payments.all().order_by('-payment_date')[:10]
    
    context = {
        'customer': customer,
        'orders': orders,
        'invoices': invoices,
        'payments': payments,
        'total_orders': customer.get_total_orders(),
        'total_spent': customer.get_total_spent(),
    }
    
    return render(request, 'customers/customer_detail.html', context)


@login_required
def customer_create(request):
    """
    Création d'un nouveau client
    """
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'Client "{customer.full_name}" créé avec succès.')
            return redirect('customers:customer_detail', customer_id=customer.id)
        else:
            messages.error(request, 'Erreur lors de la création du client. Veuillez corriger les erreurs.')
    else:
        form = CustomerForm()
    
    context = {
        'form': form,
        'title': 'Nouveau client',
        'submit_text': 'Créer le client'
    }
    
    return render(request, 'customers/customer_form.html', context)


@login_required
def customer_update(request, customer_id):
    """
    Modification d'un client existant
    """
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'Client "{customer.full_name}" modifié avec succès.')
            return redirect('customers:customer_detail', customer_id=customer.id)
        else:
            messages.error(request, 'Erreur lors de la modification du client. Veuillez corriger les erreurs.')
    else:
        form = CustomerForm(instance=customer)
    
    context = {
        'form': form,
        'customer': customer,
        'title': f'Modifier {customer.full_name}',
        'submit_text': 'Enregistrer les modifications'
    }
    
    return render(request, 'customers/customer_form.html', context)


@login_required
def customer_delete(request, customer_id):
    """
    Suppression d'un client
    """
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'POST':
        customer_name = customer.full_name
        customer.delete()
        messages.success(request, f'Client "{customer_name}" supprimé avec succès.')
        return redirect('customers:customer_list')
    
    # Vérification des dépendances
    has_orders = customer.orders.exists()
    has_invoices = customer.invoices.exists()
    has_payments = customer.payments.exists()
    
    context = {
        'customer': customer,
        'has_orders': has_orders,
        'has_invoices': has_invoices,
        'has_payments': has_payments,
        'can_delete': not (has_orders or has_invoices or has_payments)
    }
    
    return render(request, 'customers/customer_confirm_delete.html', context)


@login_required
def customer_toggle_status(request, customer_id):
    """
    Activation/désactivation d'un client
    """
    if request.method == 'POST':
        customer = get_object_or_404(Customer, id=customer_id)
        customer.is_active = not customer.is_active
        customer.save()
        
        status = "activé" if customer.is_active else "désactivé"
        messages.success(request, f'Client "{customer.full_name}" {status} avec succès.')
        
        return JsonResponse({
            'success': True,
            'is_active': customer.is_active,
            'message': f'Client {status} avec succès.'
        })
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'})


@login_required
def customer_quick_search(request):
    """
    Recherche rapide de clients pour les formulaires
    """
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
