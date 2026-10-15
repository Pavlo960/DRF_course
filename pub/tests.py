from decimal import Decimal

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, MenuItem, Order


class BeerHubAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_user('barman', password='pass12345', is_staff=True)
        cls.alice = User.objects.create_user('alice', password='pass12345')
        cls.bob = User.objects.create_user('bob', password='pass12345')

        cls.draft = Category.objects.create(name='Draft Beer')
        cls.snacks = Category.objects.create(name='Pub Snacks')
        cls.ale = MenuItem.objects.create(
            name='Lviv Golden Ale', category=cls.draft,
            description='Crisp ale', price_per_liter=Decimal('85.00'),
        )
        cls.stout = MenuItem.objects.create(
            name='Oatmeal Stout', category=cls.draft,
            description='Dark beer', price_per_liter=Decimal('95.00'), available=False,
        )
        cls.pretzel = MenuItem.objects.create(
            name='Pretzel', category=cls.snacks,
            description='Warm pretzel', price_per_liter=Decimal('55.00'),
        )

        cls.alice_order = Order.objects.create(
            menu_item=cls.ale, volume=Decimal('0.50'), price_per_liter=cls.ale.price_per_liter,
            customer_name='Alice', owner=cls.alice,
        )
        cls.bob_order = Order.objects.create(
            menu_item=cls.ale, volume=Decimal('1.00'), price_per_liter=cls.ale.price_per_liter,
            customer_name='Bob', owner=cls.bob,
        )


class MenuItemTests(BeerHubAPITestCase):
    list_url = reverse('menuitem-list')

    def test_anonymous_can_list_menu(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_filter_by_category_id_and_name(self):
        by_id = self.client.get(self.list_url, {'category': self.snacks.id})
        by_name = self.client.get(self.list_url, {'category': 'draft'})
        self.assertEqual([i['name'] for i in by_id.data], ['Pretzel'])
        self.assertEqual(len(by_name.data), 2)

    def test_regular_user_cannot_create_menu_item(self):
        self.client.force_authenticate(self.alice)
        response = self.client.post(self.list_url, {
            'name': 'New', 'description': 'x', 'price_per_liter': '10.00',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create_menu_item(self):
        self.client.force_authenticate(self.staff)
        response = self.client.post(self.list_url, {
            'name': 'New', 'description': 'x', 'price_per_liter': '10.00', 'category': self.draft.id,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['category_name'], 'Draft Beer')

    def test_price_must_be_positive(self):
        self.client.force_authenticate(self.staff)
        response = self.client.post(self.list_url, {
            'name': 'Free', 'description': 'x', 'price_per_liter': '0',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OrderTests(BeerHubAPITestCase):
    list_url = reverse('order-list')

    def test_anonymous_cannot_see_orders(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_sees_only_own_orders(self):
        self.client.force_authenticate(self.alice)
        response = self.client.get(self.list_url)
        self.assertEqual([o['id'] for o in response.data], [self.alice_order.id])

    def test_staff_sees_all_orders(self):
        self.client.force_authenticate(self.staff)
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data), 2)

    def test_user_cannot_access_foreign_order(self):
        self.client.force_authenticate(self.alice)
        url = reverse('order-detail', args=[self.bob_order.id])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_create_order_sets_owner_and_total_price(self):
        self.client.force_authenticate(self.alice)
        response = self.client.post(self.list_url, {'menu_item': self.ale.id, 'volume': 1.5}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['total_price'], '127.50')
        self.assertEqual(response.data['customer_name'], 'alice')
        self.assertEqual(Order.objects.get(id=response.data['id']).owner, self.alice)

    def test_invalid_volume_rejected(self):
        self.client.force_authenticate(self.alice)
        for volume in [0.3, 3]:
            response = self.client.post(self.list_url, {'menu_item': self.ale.id, 'volume': volume}, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('volume', response.data)

    def test_unavailable_item_cannot_be_ordered(self):
        self.client.force_authenticate(self.alice)
        response = self.client.post(self.list_url, {'menu_item': self.stout.id, 'volume': 0.5}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_my_orders(self):
        self.client.force_authenticate(self.staff)
        Order.objects.create(
            menu_item=self.ale, volume=Decimal('0.25'), price_per_liter=self.ale.price_per_liter,
            customer_name='Barman', owner=self.staff,
        )
        response = self.client.get(reverse('order-my'))
        self.assertEqual(len(response.data), 1)

    def test_filter_by_volume(self):
        self.client.force_authenticate(self.staff)
        response = self.client.get(self.list_url, {'volume': 0.5})
        self.assertEqual([o['id'] for o in response.data], [self.alice_order.id])


class OrderLifecycleTests(BeerHubAPITestCase):
    def detail_url(self, order):
        return reverse('order-detail', args=[order.id])

    def test_menu_price_change_does_not_affect_existing_orders(self):
        self.ale.price_per_liter = Decimal('200.00')
        self.ale.save()
        self.client.force_authenticate(self.alice)
        response = self.client.get(self.detail_url(self.alice_order))
        self.assertEqual(response.data['price_per_liter'], '85.00')
        self.assertEqual(response.data['total_price'], '42.50')

    def test_changing_menu_item_takes_new_price(self):
        self.client.force_authenticate(self.alice)
        response = self.client.patch(self.detail_url(self.alice_order), {'menu_item': self.pretzel.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['price_per_liter'], '55.00')

    def test_new_order_has_status_new(self):
        self.client.force_authenticate(self.alice)
        response = self.client.post(reverse('order-list'), {'menu_item': self.ale.id, 'volume': 0.5}, format='json')
        self.assertEqual(response.data['status'], 'new')

    def test_customer_cannot_change_status(self):
        self.client.force_authenticate(self.alice)
        response = self.client.patch(self.detail_url(self.alice_order), {'status': 'served'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_staff_can_change_status(self):
        self.client.force_authenticate(self.staff)
        response = self.client.patch(self.detail_url(self.alice_order), {'status': 'preparing'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'preparing')

    def test_customer_cannot_edit_or_delete_processed_order(self):
        Order.objects.filter(id=self.alice_order.id).update(status=Order.STATUS_PREPARING)
        self.client.force_authenticate(self.alice)
        url = self.detail_url(self.alice_order)
        self.assertEqual(self.client.patch(url, {'volume': 1}, format='json').status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)
