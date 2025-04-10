from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.http import HttpResponse, JsonResponse
from .models import Product, Production, ProductionHistory, Invoice, InvoiceItem, reg, login,Factorysale
from .forms import ProductionForm, ProductForm, InvoiceForm,FactorySaleForm
from django.db import transaction,IntegrityError
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth import logout
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from django.db.models import Max
from datetime import datetime
import re
from django.db import connection
from django.http import HttpResponseNotAllowed
from django.views.decorators.cache import never_cache
from django.utils.timezone import now
from django.db.models import Sum,F
from decimal import Decimal,InvalidOperation



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
    products = Product.objects.all().order_by('price')  # Sorting by price (ascending)
    return render(request, 'Stock_list.html', {'products': products})

def production_history(request):
    history = ProductionHistory.objects.all()
    return render(request, 'production_history.html', {'history': history})


def get_stock(request, product_id=None):
    try:
        if product_id:
            product = Product.objects.get(id=product_id)
            return JsonResponse({'product_name': product.name, 'stock': product.quantity})
        
        # ✅ Sort products by price (ascending order)
        products = Product.objects.all().order_by('price').values('id', 'name', 'price', 'quantity')
        return JsonResponse({'products': list(products)})

    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)


def createinvoice(request):  
    invoice_form = InvoiceForm(request.POST or None)

    if request.method == 'POST':
        if invoice_form.is_valid():
            try:
                with transaction.atomic():
                    invoice = invoice_form.save(commit=False)
                    invoice.invoice_number = ""  # Temporary invoice number
                    invoice.save()

                    products = request.POST.getlist('products[]')
                    quantities = request.POST.getlist('quantities[]')
                    accessory_quantities = request.POST.getlist('accessory_quantity')
                    accessory_prices = request.POST.getlist('accessory_price')
                    e_way = request.POST.get('e_way', "0")
                    sp_discount = request.POST.get("sp_discount","0")

                    # Convert e_way to Decimal
                    try:
                        e_way = Decimal(str(e_way).strip()) if e_way.strip() else Decimal(0)
                    except ValueError:
                        messages.error(request, "Invalid transportation charge entered.")
                        invoice.delete()
                        return redirect('createinvoice')
                    
                    try:
                        sp_discount = Decimal(str(sp_discount).strip()) if sp_discount.strip() else Decimal(0)
                    except InvalidOperation:
                        messages.error(request, "Invalid special discount entered.")
                        return redirect('createinvoice')

                    if not any(products) and not any(accessory_prices):
                        messages.error(request, "Please add at least one product or accessory.")
                        invoice.delete()
                        return redirect('createinvoice')

                    product_total = Decimal(0)  
                    accessory_total = Decimal(0)  
                    valid_items = 0  

                    # Process products
                    for i in range(len(products)):
                        try:
                            product_id = products[i].strip()
                            quantity = int(quantities[i].strip()) if quantities[i].strip() else 0

                            if product_id and quantity > 0:
                                product = get_object_or_404(Product, id=product_id)

                                if product.quantity >= quantity:
                                    price = Decimal(str(product.price))
                                    subtotal = price * quantity
                                    product_total += subtotal  

                                    InvoiceItem.objects.create(
                                        invoice=invoice,
                                        product=product,
                                        quantity=quantity,
                                        price=price,
                                        subtotal=subtotal
                                    )
                                    product.quantity -= quantity  
                                    product.save()
                                    valid_items += 1
                                else:
                                    messages.warning(request, f"Not enough stock for {product.name}. Skipped.")

                        except (ValueError, Product.DoesNotExist) as e:
                            messages.error(request, f"Invalid product selection: {e}")
                            invoice.delete()
                            return redirect('createinvoice')

                    # Process accessories
                    for j in range(len(accessory_prices)):
                        try:
                            accessory_price = Decimal(str(accessory_prices[j]).strip()) if accessory_prices[j].strip() else Decimal(0)
                            accessory_quantity = int(accessory_quantities[j].strip()) if accessory_quantities[j].strip() else 0

                            if accessory_price > 0 and accessory_quantity > 0:
                                subtotal = accessory_price
                                accessory_total += subtotal  

                                InvoiceItem.objects.create(
                                    invoice=invoice,
                                    product=None,  # No product for accessories
                                    quantity=accessory_quantity,
                                    price=accessory_price,
                                    subtotal=subtotal
                                )
                                valid_items += 1

                        except ValueError as e:
                            messages.error(request, f"Invalid accessory price or quantity entered: {e}")
                            invoice.delete()
                            return redirect('createinvoice')

                    if valid_items == 0:
                        invoice.delete()  
                        messages.error(request, "No valid items to create an invoice.")
                        return redirect('createinvoice')

                    # Apply discount ONLY to product total
                    discount_percentage = Decimal(str(invoice.discount_percentage or 0))
                    discount_amount = (product_total * discount_percentage) / Decimal(100)
                    final_product_total = product_total - discount_amount

                    # Final amount calculation with Decimal
                    final_amount = final_product_total + accessory_total + e_way - sp_discount

                    # Debugging print statements
                    print(f"Product Total: {product_total}, Discount Amount: {discount_amount}, Final Product Total: {final_product_total}")
                    print(f"Accessory Total: {accessory_total}, Transport Charge (e_way): {e_way}, Final Amount: {final_amount}")

                    invoice.total_amount = final_amount
                    invoice.e_way = e_way  
                    invoice.save()

                    messages.success(request, f"Invoice {invoice.invoice_number} created successfully!")
                    return redirect('invoicelist')

            except IntegrityError as e:
                messages.error(request, f"Invoice creation failed due to a system error: {e}")
            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {e}")

    products = Product.objects.all().order_by('price')
    return render(request, 'create invoice.html', {  
        'invoice_form': invoice_form,
        'products': products,
    })

def invoice_list(request):
    invoices = Invoice.objects.all().order_by('-date','-id')  # Order by date (newest first)
    return render(request, 'invoice list.html', {'invoices': invoices})

def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    items = InvoiceItem.objects.filter(invoice=invoice).order_by('price')
    total_qty = sum(item.quantity for item in items if item.product) 
    subtotal = sum(item.quantity * item.price for item in items)
    discount_amount = (subtotal * invoice.discount_percentage) / 100 if invoice.discount_percentage else 0
    accessory=Invoice.accessory_price
    accessory = Decimal(getattr(invoice, "accessory_price", 0)) 
    e_way=Invoice.e_way
    e_way = Decimal(getattr(invoice, "e_way", 0))
    sp_discount = Invoice.sp_discount
    sp_discount = Decimal(getattr(invoice, "sp_discount", 0)) 
    total_amount = subtotal - discount_amount + accessory + e_way
    context = {
        'invoice': invoice,
        'items': items,
        'subtotal': subtotal,
        'discount_amount': discount_amount,
        'total_amount': total_amount,
        'total_qty': total_qty,
        'accessory':accessory,
        'e_way':e_way,
        'sp_discount':sp_discount,
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
            elif l.utype == "admin":
                request.session["uid"] = l.uid_id
                return HttpResponse("<script>alert('Welcome Admin');window.location='/adminhome';</script>")

        except login.DoesNotExist:
            return HttpResponse("<script>alert('Invalid username or password.');window.location='/login';</script>")

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

@never_cache
def userhome(request):
    template = loader.get_template("userhome.html")
    context = {}
    return HttpResponse(template.render(context, request))

def logoutview(request):
    logout(request)  # Logs out the user
    request.session.flush()  # Clears session data

    response = redirect('login')  # Redirects to login page
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response

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



def delete_invoice(request, invoice_id):
    if request.method == 'POST':  # Only allow POST
        invoice = get_object_or_404(Invoice, id=invoice_id)

        invoice_items = InvoiceItem.objects.filter(invoice=invoice)
        for item in invoice_items:
            if item.product: 
                item.product.quantity += item.quantity
                item.product.save() 

        invoice.delete()  # Now delete the invoice
        messages.success(request, f"Invoice {invoice.invoice_number} deleted successfully! Product stock has been updated.")
        return HttpResponse("<script>alert('Invoice deleted successfully! Product stock has been updated.');window.location='/invoicelist';</script>")

    return HttpResponseNotAllowed(['POST']) 


def adminhome(request):
    template = loader.get_template("adminhome.html")
    context = {}
    return HttpResponse(template.render(context, request))

def sales_report(request):
    invoices = Invoice.objects.all()
    factory_sales = Factorysale.objects.all()
    today = now().date()
    start_date = request.GET.get('start_date', today)
    end_date = request.GET.get('end_date', today)

    # Apply filtering if both dates are provided
    if start_date and end_date:
        invoices = invoices.filter(date__range=[start_date, end_date])
        factory_sales = factory_sales.filter(date__range=[start_date, end_date])

    # Calculate total sales from both Invoice and Factorysale tables
    total_invoice_sales = sum(invoice.total_amount for invoice in invoices)
    total_factory_sales = sum(factory_sale.total_amount for factory_sale in factory_sales)

    # Overall total sales
    total_sales = total_invoice_sales + total_factory_sales

    context = {
        'invoices': invoices,
        'factory_sales': factory_sales,
        'total_invoice_sales': total_invoice_sales,
        'total_factory_sales': total_factory_sales,
        'total_sales': total_sales,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'sales_report.html', context)

def product_sales_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if not start_date:
        start_date = datetime.today().date()
    else:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            return render(request, "product_sales_report.html", {"error": "Invalid start date format"})

    if not end_date:
        end_date = datetime.today().date()
    else:
        try:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return render(request, "product_sales_report.html", {"error": "Invalid end date format"})
    sales_data = (
        InvoiceItem.objects
        .filter(invoice__date__range=[start_date, end_date]) 
        .values('product__name') 
        .annotate(
            total_quantity=Sum('quantity'), 
        )
        .order_by('-total_quantity')
    )
    return render(request, "product_sales_report.html", {
        "sales_data": sales_data,
        "start_date": start_date,
        "end_date": end_date
    })

def stock_edit(request):
    """View to display and edit stock list by the admin"""
    products = Product.objects.all()

    if request.method == "POST":
        for product in products:
            field_name = f'quantity_{product.id}'
            if field_name in request.POST:
                new_quantity = request.POST[field_name]
                try:
                    new_quantity = int(new_quantity)
                    if new_quantity >= 0:
                        product.quantity = new_quantity
                        product.save()
                    else:
                        messages.error(request, f"Invalid quantity for {product.name}")
                except ValueError:
                    messages.error(request, f"Invalid input for {product.name}")

        messages.success(request, "Stock updated successfully!")
        return redirect('stock_edit')  # Redirect to avoid resubmission

    return render(request, 'stock_edit.html', {'products': products})

import json
from decimal import Decimal

def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def edit_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)

    if request.method == "POST":
        try:
            customer = request.POST.get("customer", invoice.customer)
            date = request.POST.get("date", invoice.date)
            discount_percentage = request.POST.get("discount_percentage", invoice.discount_percentage)

            # Convert discount percentage to Decimal
            discount_percentage = Decimal(discount_percentage) if discount_percentage else Decimal(0)

            product_ids = request.POST.getlist("products[]")
            quantities = request.POST.getlist("quantities[]")

            if not product_ids or not quantities:
                return JsonResponse({"success": False, "message": "Products and quantities are required."})

            if len(product_ids) != len(quantities):
                return JsonResponse({"success": False, "message": "Mismatched product and quantity count."})

            # ✅ Restore stock before deleting old invoice items
            for item in invoice.invoice_items.all():
                if item.product:
                    item.product.quantity += item.quantity
                    item.product.save()

            # ✅ Clear existing invoice items (excluding accessory items)
            invoice.invoice_items.all().delete()

            # ✅ Process new items
            product_total = Decimal(0)
            skipped_items = []
            for product_id, quantity in zip(product_ids, quantities):
                product = Product.objects.filter(id=product_id).first()

                if not product:
                    skipped_items.append(f"Product ID {product_id} not found")
                    continue

                try:
                    quantity = int(quantity)
                except ValueError:
                    skipped_items.append(f"Invalid quantity for {product.name}")
                    continue

                if product.quantity < quantity:
                    skipped_items.append(f"Not enough stock for {product.name}")
                    continue

                price = product.price
                subtotal = price * quantity
                product_total += subtotal

                # ✅ Deduct the new quantity from stock
                product.quantity -= quantity
                product.save()

                # ✅ Create new invoice item
                InvoiceItem.objects.create(
                    invoice=invoice,
                    product=product,
                    quantity=quantity,
                    price=price,
                    subtotal=subtotal,
                )

            # ✅ Apply discount only to product total
            discount_amount = (product_total * discount_percentage) / Decimal(100)
            final_product_total = product_total - discount_amount

            # ✅ Final total = product total after discount + fixed accessory and e-way charges
            final_amount = final_product_total + invoice.accessory_price + invoice.e_way - invoice.sp_discount

            # ✅ Update invoice details
            invoice.customer = customer
            invoice.date = date
            invoice.discount_percentage = discount_percentage
            invoice.total_amount = final_amount
            invoice.save()

            if skipped_items:
                skipped_message = f"Invoice updated, but some items were skipped due to issues: {', '.join(skipped_items)}"
                return HttpResponse(f"<script>alert('{skipped_message}');window.location='/invoicelist';</script>")
            else:
                return HttpResponse("<script>alert('Invoice Updated successfully!');window.location='/invoicelist';</script>")

        except ValueError:
            return JsonResponse({"success": False, "message": "Invalid number format."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    # ✅ Load data for rendering
    invoice_items = InvoiceItem.objects.filter(invoice=invoice, product__isnull=False)
    products = Product.objects.exclude(name__icontains='Accessory')

    invoice_data = {
        "id": invoice.id,
        "customer": str(invoice.customer),
        "date": invoice.date.strftime("%Y-%m-%d"),
        "discount": float(invoice.discount_percentage) if invoice.discount_percentage else 0.0,
        "total": float(invoice.total_amount) if invoice.total_amount else 0.0,
        "items": [
            {
                "product_id": item.product.id,
                "quantity": item.quantity,
                "price": float(item.price),
                "subtotal": float(item.subtotal),
            } for item in invoice_items
        ]
    }

    return render(request, 'Edit invoice.html', {
        'invoice': invoice,
        'invoice_json': json.dumps(invoice_data),
        'products': products
    })



def create_factory_sale(request):
    if request.method == 'POST':
        form = FactorySaleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Factory Sale added successfully!")
            return redirect('factorysalelist')  
        else:
            messages.error(request, "Error in form submission.")

    else:
        form = FactorySaleForm()

    return render(request, 'create_factory_sale.html', {'form': form})

def factory_sale_list(request):
    sales = Factorysale.objects.all().order_by('-date')
    return render(request, 'factory_sale_list.html', {'sales': sales})

def delete_factory_sale(request, sale_id):
    sale = get_object_or_404(Factorysale, id=sale_id)
    sale.delete()
    messages.success(request, "Factory Sale deleted successfully!")
    return redirect('factorysalelist')