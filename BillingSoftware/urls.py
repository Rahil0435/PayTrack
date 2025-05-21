"""
URL configuration for BillingSoftware project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
import app.views
import app2.views
from django.http import HttpResponseNotFound
from django.views.generic import RedirectView

def favicon_view(request):
    return HttpResponseNotFound()



urlpatterns = [
    path('admin/', admin.site.urls),
    path("favicon.ico", RedirectView.as_view(url="/static/favicon.ico", permanent=True)),
    path('', app.views.Home, name='home'),
    path('form/', app.views.registration, name='form'),
    path('login/', app.views.Login, name='login'),
    path('userhome/', app.views.userhome, name='userhome'),
    path('adminhome/', app.views.adminhome, name='adminhome'),
    path('addproduct/',app. views.add_product, name='addproduct'),
    path('addproduction/',app. views.add_production, name='addproduction'),
    path('productlist/',app.views.product_list, name='productlist'),
    path('productionhistory/', app.views.production_history, name='productionhistory'),
    path('get_stock/<int:product_id>/',app.views.get_stock, name='get_stock'),
    path('createinvoice/',app.views.createinvoice,name='createinvoice'),
    path('invoicelist/',app.views.invoice_list, name='invoicelist'),
    path('invoice/<int:invoice_id>/',app.views.invoice_detail, name='invoice_detail'),
    path('logout/',app.views.logoutview, name='logout'),
    path('invoice/<int:invoice_id>/pdf/',app.views.generate_pdf, name='generate_pdf'),
    path('invoice/delete/<int:invoice_id>/',app.views.delete_invoice, name='delete_invoice'),
    path('salesreport/',app.views.sales_report, name='salesreport'),
    path('product_sales_report/',app.views.product_sales_report, name='product_sales_report'),
    path('stock_edit/',app.views.stock_edit, name='stock_edit'), 
    path('editinvoice/<int:invoice_id>/',app.views.edit_invoice, name='editinvoice'), 
    path('factorysale/',app.views.create_factory_sale, name='factorysale'),
    path('factorysalelist/',app.views.factory_sale_list, name='factorysalelist'),
    path('factorysale/delete/<int:sale_id>/',app.views.delete_factory_sale, name='delete_factory_sale'),
    path('addcustomer/',app.views.addcustomer,name='addcustomer'),
    path('viewcustomer/', app.views.customer_list,name='viewcustomer'),
    path('location_report/',app.views.location_report, name='locationreport'),
    path('export-invoices-to-excel/',app.views.export_invoices_to_excel, name='export_invoices_to_excel'),
    path('transaction_report/',app.views.transaction_report, name='transaction_report'),
    path('delete_transaction/<int:payment_id>/',app.views.delete_transaction, name='delete_transaction'),
    path('delete_customer/<int:customer_id>/',app.views.delete_customer, name='delete_customer'),
    path('update_advance/<int:customer_id>/',app.views.update_advance_amount, name='update_advance'),
    path('advance-usage-report/', app.views.advance_usage_report, name='advance_usage_report'),
    
    path('login2/', app2.views.Login2, name='login2'),
    path('form2/', app2.views.registration2, name='form2'),
    path('userhome2/', app2.views.userhome2, name='userhome2'),
    path('addproduct2/',app2.views.add_product2, name='addproduct2'),
    path('addproduction2/',app2.views.add_production2, name='addproduction2'),
    path('productlist2/',app2.views.product_list2, name='productlist2'),
    path('productionhistory2/', app2.views.production_history2, name='productionhistory2'),
    path('get_stock2/<int:product_id>/',app2.views.get_stock2, name='get_stock2'),
    path('createinvoice2/',app2.views.createinvoice2,name='createinvoice2'),
    path('invoicelist2/',app2.views.invoice_list2, name='invoicelist2'),
    path('invoice2/<int:invoice_id>/',app2.views.invoice_detail2, name='invoice_detail2'),
    path('logout2/',app2.views.logoutview2, name='logout2'),
    path('invoice2/<int:invoice_id>/pdf/',app2.views.generate_pdf2, name='generate_pdf2'),
    path('invoice2/delete/<int:invoice_id>/',app2.views.delete_invoice2, name='delete_invoice2'),
    path('salesreport2/',app2.views.sales_report2, name='salesreport2'),
    path('product_sales_report2/',app2.views.product_sales_report2, name='product_sales_report2'),
    path('stock_edit2/',app2.views.stock_edit2, name='stock_edit2'), 
    path('editinvoice2/<int:invoice_id>/',app2.views.edit_invoice2, name='editinvoice2'),
    path('factorysale2/',app2.views.create_factory_sale2, name='factorysale2'),
    path('factorysalelist2/',app2.views.factory_sale_list2, name='factorysalelist2'),
    path('factorysale/delete2/<int:sale_id>/',app2.views.delete_factory_sale2, name='delete_factory_sale2'),
    path('adminhome2/', app2.views.adminhome2, name='adminhome2'),
    path('addcustomer2/',app2.views.addcustomer2,name='addcustomer2'),
    path('viewcustomer2/', app2.views.customer2_list,name='viewcustomer2'),
    path('location_report2/',app2.views.location_report2, name='locationreport2'),
    path('export-invoices-to-excel2/',app2.views.export_invoices_to_excel2, name='export_invoices_to_excel2'),
    path('transaction_report2/',app2.views.transaction_report2, name='transaction_report2'),
    path('delete_transaction2/<int:payment_id>/',app2.views.delete_transaction2, name='delete_transaction2'),
    path('delete_customer2/<int:customer_id>/',app2.views.delete_customer2, name='delete_customer2'),
    path('update_advance2/<int:customer_id>/',app2.views.update_advance_amount2, name='update_advance2'),
    path('advance-usage-report2/', app2.views.advance_usage_report2, name='advance_usage_report2'),





] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
