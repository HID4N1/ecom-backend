from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from .models import Product, Pack, PackProduct

User = get_user_model()


class APITestCase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin',
            password='password',
            role='admin',
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='password',
            role='customer',
        )

    def authenticate(self, user):
        response = self.client.post(
            '/api/token/',
            {'username': user.username, 'password': 'password'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_create_product(self):
        self.authenticate(self.admin)
        response = self.client.post(
            '/api/products/',
            {'name': 'Test Product', 'description': 'Test Description', 'price': '10.99', 'stock': 100},
            format='json',
        )
        self.assertEqual(response.status_code, 201)

    def test_commerce_data_is_public(self):
        response = self.client.get('/api/commerce/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('productCollections', response.data)
        self.assertIn('curatedPacks', response.data)
        self.assertEqual(response.data['productCollections'][0]['products'][0]['id'], 'clear-26')

    def test_products_are_public(self):
        Product.objects.create(
            name='CLEAR 26',
            description='Découverte - CLEAR - 26 bandes',
            price='159.00',
            stock=100,
        )

        response = self.client.get('/api/products/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['name'], 'CLEAR 26')

    def test_packs_are_public(self):
        product = Product.objects.create(
            name='CLEAR 26',
            description='Découverte - CLEAR - 26 bandes',
            price='159.00',
            stock=100,
        )
        Pack.objects.create(
            title='Pack Duo',
            description='Le meilleur équilibre entre sommeil et performance.',
            price='300.00',
            includes=['1 boîte CLEAR (26)', '1 boîte TAN (26)'],
        )
        pack = Pack.objects.get(title='Pack Duo')
        PackProduct.objects.create(pack=pack, product=product, quantity=1)

        response = self.client.get('/api/packs/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['title'], 'Pack Duo')
        self.assertEqual(response.data[0]['price_label'], '300 DH')
        self.assertEqual(response.data[0]['products'][0]['product']['name'], 'CLEAR 26')

    def test_customer_can_update_own_cart(self):
        product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price='10.99',
            stock=100,
        )
        self.authenticate(self.user)
        response = self.client.post(
            '/api/cart/',
            {'items': [{'product': product.id, 'quantity': 2}]},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['items'][0]['quantity'], 2)

    def test_customer_can_create_order(self):
        product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price='10.99',
            stock=100,
        )
        self.authenticate(self.user)
        response = self.client.post(
            '/api/orders/',
            {'items': [{'product': product.id, 'quantity': 2, 'price': '10.99'}]},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['total_price'], '21.98')
