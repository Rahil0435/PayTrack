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
    path('addproduct/',app. views.add_product, name='addproduct'),
    path('addproduction/',app. views.add_production, name='addproduction'),
    path('productlist/',app.views.product_list, name='productlist'),
    path('productionhistory/', app.views.production_history, name='productionhistory'),
    path('get_stock/<int:product_id>/',app.views.get_stock, name='get_stock'),
    path('createinvoice/',app.views.create_invoice,name='createinvoice'),
    path('invoicelist/',app.views.invoice_list, name='invoicelist'),
    path('invoice/<int:invoice_id>/',app.views.invoice_detail, name='invoice_detail'),
    path('logout/',app.views.logoutview, name='logout'),
    path('invoice/<int:invoice_id>/pdf/',app.views.generate_pdf, name='generate_pdf'),
    path("db-status/", app.views.db_status, name="db_status"),
    path('invoice/delete/<int:invoice_id>/',app.views.delete_invoice, name='delete_invoice'),


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
