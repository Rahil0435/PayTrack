from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.http import HttpResponse, JsonResponse
from .models import Product, Production, ProductionHistory, Invoice, InvoiceItem, reg, login
from .forms import ProductionForm, ProductForm, InvoiceForm
from django.db import transaction
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth import logout
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from django.db.models import Max
from django.utils import timezone
import re
from django.db import connection



# Create your views here.
def Home(request):
    template = loader.get_template("base.html")
    context = {}
    return HttpResponse(template.render(context, request))

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('productlist')
    else:
        form = ProductForm()
    return render(request, 'add product.html', {'form': form})

def add_production(request):
    if request.method == 'POST':
        form = ProductionForm(request.POST)
        if form.is_valid():
            production = form.save(commit=False)  # Save the form but don't commit yet
            product = production.product  # Get the associated product

            # Debugging output: Before update
            print(f"Before update: Product {product.name} quantity: {product.quantity}")

            # Ensure product quantity is only updated for a new production record
            if not production.pk:  # Check if this is a new record (unsaved)
                product.quantity + production.quantity_added  # Update stock quantity
                product.save()  # Save the product changes

                # Debugging output: After update
                print(f"After update: Product {product.name} quantity: {product.quantity}")
            else:
                print(f"No stock update needed. Production record already exists.")

            production.save()  # Save the production record

            # Debugging output: Production saved
            print(f"Production saved: ID={production.id}, Product={product.name}, Quantity Added={production.quantity_added}")

            # Add production history
            ProductionHistory.objects.create(
                product=product,
                quantity_produced=production.quantity_added,
                date=production.date
            )

            # Debugging output: Production history saved
            print(f"Production history saved for product {product.name} with quantity {production.quantity_added}")

            return redirect('productlist')  # Redirect to product list after successful save
    else:
        form = ProductionForm()

    return render(request, 'addproduction.html', {'form': form})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'Stock_list.html', {'products': products})

def production_history(request):
    history = ProductionHistory.objects.all()
    return render(request, 'production_history.html', {'history': history})

def get_stock(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        return JsonResponse({'stock': product.quantity})  
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)

def create_invoice(request):
    products = Product.objects.all()  # Fetch all products for dropdown selection

    # Get the last invoice number and increment it
    last_invoice = Invoice.objects.aggregate(Max('invoice_number'))
    last_invoice_number = last_invoice['invoice_number__max']
    new_invoice_number = last_invoice_number + 1 if last_invoice_number else 1001  # Start from 1001 if no invoices exist

    if request.method == 'POST':
        form = InvoiceForm(request.POST)

        if form.is_valid():
            customer_name = form.cleaned_data['customer']
            date = form.cleaned_data['date']
            discount_percentage = form.cleaned_data.get('discount_percentage', 0)

            # Create the invoice with the new invoice number
            invoice = Invoice.objects.create(
                invoice_number=new_invoice_number,
                customer=customer_name,
                date=date,
                discount_percentage=discount_percentage
            )

            total_amount = 0  # Track total amount before discount

            products_selected = request.POST.getlist('products[]')
            quantities = request.POST.getlist('quantities[]')

            for product_id, quantity in zip(products_selected, quantities):
                product = Product.objects.get(id=product_id)
                quantity = int(quantity)
                subtotal = product.price * quantity
                total_amount += subtotal

                # Create invoice item
                InvoiceItem.objects.create(
                    invoice=invoice,
                    product=product,
                    quantity=quantity,
                    price=product.price,
                    subtotal=subtotal
                )

            # Apply discount
            discount_amount = (total_amount * discount_percentage) / 100
            final_total = total_amount - discount_amount
            invoice.total_amount = final_total
            invoice.save()

            messages.success(request, f'Invoice #{invoice.invoice_number} created successfully!')
            return redirect('invoice_list')  # Redirect to the invoice list page

        else:
            messages.error(request, 'There was an error in the form submission.')

    else:
        form = InvoiceForm()

    return render(request, 'create_invoice.html', {'form': form, 'products': products, 'invoice_number': new_invoice_number})


def invoice_list(request):
    invoices = Invoice.objects.all().order_by('-date')
    paginator = Paginator(invoices, 10)  # Paginate with 10 invoices per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'invoice list.html', {'page_obj': page_obj})

def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    items = InvoiceItem.objects.filter(invoice=invoice)

    subtotal = sum(item.quantity * item.price for item in items)
    discount_amount = (subtotal * invoice.discount_percentage) / 100 if invoice.discount_percentage else 0
    total_amount = subtotal - discount_amount
    context = {
        'invoice': invoice,
        'items': items,
        'subtotal': subtotal,
        'discount_amount': discount_amount,
        'total_amount': total_amount,
    }
    return render(request, 'invoice details.html', context)

def Login(request):
    if request.method == 'POST':
        uname = request.POST.get("uname")
        psw = request.POST.get("pswd")
        try:
            l = login.objects.get(uname=uname, pswd=psw)
            if l.utype == "user":
                request.session["uid"] = l.uid_id
                return HttpResponse("<script>alert('Welcome User');window.location='/userhome';</script>")

        except login.DoesNotExist:
            messages.error(request, "Invalid username or password.")
            return redirect('/login')

    template = loader.get_template("login.html")
    context = {}
    return HttpResponse(template.render(context, request))

def registration(request):
    if request.method == "POST":
        r = reg()
        r.name = request.POST.get("Name")
        r.phno = request.POST.get("phno")
        r.save()
        id = reg.objects.latest("id").id
        l = login()
        l.uname = request.POST.get("uname")
        l.pswd = request.POST.get("psw")
        l.utype = 'user'
        l.uid_id = id
        l.save()
        return HttpResponse("<script>alert('Registered successfully');window.location='/login';</script>")

    template = loader.get_template("reg.html")
    context = {}
    return HttpResponse(template.render(context, request))

def userhome(request):
    template = loader.get_template("userhome.html")
    context = {}
    return HttpResponse(template.render(context, request))

def logoutview(request):
    logout(request) 
    return HttpResponse("<script>alert('Logout successfully');window.location='/login';</script>")

def generate_pdf(request, invoice_id):
    # Fetch invoice data from your database
    invoice = get_object_or_404(Invoice, pk=invoice_id)  # Adjust according to your model
    items = invoice.items.all()  # Assuming items are related to the invoice

    # Render the HTML template with the invoice data
    html_content = render_to_string('invoice template.html', {'invoice': invoice, 'items': items})
    
    # Create the response and set the appropriate content type for PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
    
    # Generate the PDF from the HTML string
    pisa_status = pisa.CreatePDF(html_content, dest=response)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
    
    # Generate the PDF from the HTML string
    pisa_status = pisa.CreatePDF(html_content, dest=response)
    
    # If there are errors, return an error message
    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)

    return response


def db_status(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "Database connected!"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)