from django.test import TestCase
from django.urls import reverse
from .models import Product, Invoice, login, reg

class InvoiceViewTests(TestCase):
    def setUp(self):
        # Create a product for testing
        self.product = Product.objects.create(name="Test Product", price=10.00, quantity=100)

    def test_create_invoice_success(self):
        response = self.client.post(reverse('create_invoice'), {
            'products[]': [self.product.id],
            'quantities[]': [1],
        })
        self.assertEqual(response.status_code, 302)  # Check for redirect on success
        self.assertEqual(Invoice.objects.count(), 1)  # Check that an invoice was created

    def test_create_invoice_insufficient_stock(self):
        # Reduce stock to trigger insufficient stock error
        self.product.quantity = 0
        self.product.save()
        
        response = self.client.post(reverse('create_invoice'), {
            'products[]': [self.product.id],
            'quantities[]': [1],
        })
        self.assertEqual(response.status_code, 200)  # Check for rendering the form again
        self.assertContains(response, "Insufficient stock for product: Test Product")  # Check for error message

    def test_login_invalid_credentials(self):
        # Attempt to log in with invalid credentials
        response = self.client.post(reverse('login'), {
            'uname': 'invalid_user',
            'pswd': 'wrong_password',
        })
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertRedirects(response, '/login')  # Check redirection to login page

    def test_login_success(self):
        # Create a user for testing login
        user_reg = reg.objects.create(name="Test User", phno="1234567890")
        login.objects.create(uname="testuser", pswd="password", utype="user", uid=user_reg)

        response = self.client.post(reverse('login'), {
            'uname': 'testuser',
            'pswd': 'password',
        })
        self.assertEqual(response.status_code, 200)  # Check for successful login
        self.assertContains(response, "Welcome User")  # Check for welcome message
