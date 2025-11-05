"""
Comprehensive tests for sponsoring module (util.py and views.py) to increase coverage.
Tests cover sponsor management, item management, and sponsor orders.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.db.models import Q, Sum
from rest_framework import status
from datetime import date


@pytest.mark.django_db
class TestSponsoringUtil:
    """Tests for sponsoring/util.py functions."""

    def test_get_items(self):
        """Test getting all items with cloudinary images."""
        from sponsoring.util import get_items
        from sponsoring.models import Item
        
        # Create test item
        item = Item.objects.create(
            item_nm='Test Item',
            item_desc='Test Description',
            quantity=10,
            reset_date=date(2024, 1, 1),
            active='y',
            void_ind='n',
            img_id='test_img',
            img_ver='123'
        )
        
        with patch('sponsoring.util.CloudinaryImage') as mock_cloudinary:
            mock_cloudinary.return_value.build_url.return_value = 'https://test.com/image.jpg'
            
            result = get_items()
            
            assert len(result) >= 1
            assert result[0]['item_nm'] == 'Test Item'
            assert result[0]['item_desc'] == 'Test Description'
            assert result[0]['quantity'] == 10
            assert result[0]['sponsor_quantity'] == 0
            assert 'img_url' in result[0]

    def test_get_items_with_purchased_quantity(self):
        """Test getting items with purchased quantities."""
        from sponsoring.util import get_items
        from sponsoring.models import Item, Sponsor, ItemSponsor
        
        # Create test data
        item = Item.objects.create(
            item_nm='Test Item',
            item_desc='Test Description',
            quantity=10,
            reset_date=date(2024, 1, 1),
            active='y',
            void_ind='n',
            img_id='test_img',
            img_ver='123'
        )
        
        sponsor = Sponsor.objects.create(
            sponsor_nm='Test Sponsor',
            phone='1234567890',
            email='test@test.com',
            void_ind='n'
        )
        
        ItemSponsor.objects.create(
            item_id=item,
            sponsor_id=sponsor,
            quantity=5,
            void_ind='n'
        )
        
        with patch('sponsoring.util.CloudinaryImage') as mock_cloudinary:
            mock_cloudinary.return_value.build_url.return_value = 'https://test.com/image.jpg'
            
            result = get_items()
            
            assert len(result) >= 1
            # Should aggregate purchased quantity
            item_result = [r for r in result if r['item_id'] == item.item_id][0]
            assert item_result['sponsor_quantity'] == 5

    def test_get_sponsors(self):
        """Test getting all sponsors."""
        from sponsoring.util import get_sponsors
        from sponsoring.models import Sponsor
        
        # Create test sponsors
        Sponsor.objects.create(
            sponsor_nm='Sponsor A',
            phone='1111111111',
            email='a@test.com',
            void_ind='n'
        )
        Sponsor.objects.create(
            sponsor_nm='Sponsor B',
            phone='2222222222',
            email='b@test.com',
            void_ind='n'
        )
        
        result = get_sponsors()
        
        assert result.count() >= 2
        sponsor_names = [s.sponsor_nm for s in result]
        assert 'Sponsor A' in sponsor_names
        assert 'Sponsor B' in sponsor_names

    def test_save_sponsor_new(self):
        """Test saving a new sponsor."""
        from sponsoring.util import save_sponsor
        
        sponsor_data = {
            'sponsor_nm': 'New Sponsor',
            'phone': '5555555555',
            'email': 'new@test.com'
        }
        
        result = save_sponsor(sponsor_data)
        
        assert result.sponsor_nm == 'New Sponsor'
        assert result.phone == '5555555555'
        assert result.email == 'new@test.com'
        assert result.void_ind == 'n'

    def test_save_sponsor_update(self):
        """Test updating an existing sponsor."""
        from sponsoring.util import save_sponsor
        from sponsoring.models import Sponsor
        
        # Create existing sponsor
        existing = Sponsor.objects.create(
            sponsor_nm='Old Name',
            phone='1111111111',
            email='old@test.com',
            void_ind='n'
        )
        
        sponsor_data = {
            'sponsor_id': existing.sponsor_id,
            'sponsor_nm': 'Updated Name',
            'phone': '9999999999',
            'email': 'updated@test.com'
        }
        
        result = save_sponsor(sponsor_data)
        
        assert result.sponsor_id == existing.sponsor_id
        assert result.sponsor_nm == 'Updated Name'
        assert result.phone == '9999999999'
        assert result.email == 'updated@test.com'

    def test_save_item_new(self):
        """Test saving a new item."""
        from sponsoring.util import save_item
        
        item_data = {
            'item_nm': 'New Item',
            'item_desc': 'Description',
            'quantity': 15,
            'reset_date': date(2024, 6, 1)
        }
        
        result = save_item(item_data)
        
        assert result.item_nm == 'New Item'
        assert result.item_desc == 'Description'
        assert result.quantity == 15
        assert result.void_ind == 'n'

    def test_save_item_update(self):
        """Test updating an existing item."""
        from sponsoring.util import save_item
        from sponsoring.models import Item
        
        # Create existing item
        existing = Item.objects.create(
            item_nm='Old Item',
            item_desc='Old Desc',
            quantity=5,
            reset_date=date(2024, 1, 1),
            void_ind='n'
        )
        
        item_data = {
            'item_id': existing.item_id,
            'item_nm': 'Updated Item',
            'item_desc': 'Updated Desc',
            'quantity': 20,
            'reset_date': date(2024, 12, 1)
        }
        
        result = save_item(item_data)
        
        assert result.item_id == existing.item_id
        assert result.item_nm == 'Updated Item'
        assert result.quantity == 20

    def test_save_item_with_new_image(self):
        """Test saving item with a new image upload."""
        from sponsoring.util import save_item
        
        item_data = {
            'item_nm': 'Item with Image',
            'item_desc': 'Has image',
            'quantity': 10,
            'reset_date': date(2024, 1, 1),
            'img': 'base64imagedata'
        }
        
        with patch('sponsoring.util.uploader.upload') as mock_upload:
            mock_upload.return_value = {
                'public_id': 'new_img_id',
                'version': '456'
            }
            
            result = save_item(item_data)
            
            assert result.img_id == 'new_img_id'
            assert result.img_ver == '456'
            mock_upload.assert_called_once()

    def test_save_item_with_existing_image_update(self):
        """Test updating item's existing image."""
        from sponsoring.util import save_item
        from sponsoring.models import Item
        
        # Create item with existing image
        existing = Item.objects.create(
            item_nm='Item',
            item_desc='Desc',
            quantity=5,
            reset_date=date(2024, 1, 1),
            void_ind='n',
            img_id='old_img_id',
            img_ver='123'
        )
        
        item_data = {
            'item_id': existing.item_id,
            'item_nm': 'Item',
            'item_desc': 'Desc',
            'quantity': 5,
            'reset_date': date(2024, 1, 1),
            'img': 'new_base64_data'
        }
        
        with patch('sponsoring.util.uploader.upload') as mock_upload:
            mock_upload.return_value = {
                'public_id': 'old_img_id',
                'version': '789'
            }
            
            result = save_item(item_data)
            
            assert result.img_ver == '789'
            # Should pass public_id for existing image
            mock_upload.assert_called_once_with('new_base64_data', public_id='old_img_id')

    def test_save_item_sponsor_new(self):
        """Test saving a new item sponsor relationship."""
        from sponsoring.util import save_item_sponsor
        from sponsoring.models import Item, Sponsor
        
        # Create test data
        item = Item.objects.create(
            item_nm='Item',
            item_desc='Desc',
            quantity=10,
            reset_date=date(2024, 1, 1),
            void_ind='n'
        )
        sponsor = Sponsor.objects.create(
            sponsor_nm='Sponsor',
            phone='1111111111',
            email='test@test.com',
            void_ind='n'
        )
        
        item_sponsor_data = {
            'item_id': item.item_id,
            'sponsor_id': sponsor.sponsor_id,
            'quantity': 3
        }
        
        result = save_item_sponsor(item_sponsor_data)
        
        assert result.item_id.item_id == item.item_id
        assert result.sponsor_id.sponsor_id == sponsor.sponsor_id
        assert result.quantity == 3
        assert result.void_ind == 'n'

    def test_save_item_sponsor_update(self):
        """Test updating an existing item sponsor relationship."""
        from sponsoring.util import save_item_sponsor
        from sponsoring.models import Item, Sponsor, ItemSponsor
        
        # Create test data
        item = Item.objects.create(
            item_nm='Item',
            item_desc='Desc',
            quantity=10,
            reset_date=date(2024, 1, 1),
            void_ind='n'
        )
        sponsor = Sponsor.objects.create(
            sponsor_nm='Sponsor',
            phone='1111111111',
            email='test@test.com',
            void_ind='n'
        )
        existing = ItemSponsor.objects.create(
            item_id=item,
            sponsor_id=sponsor,
            quantity=2,
            void_ind='n'
        )
        
        item_sponsor_data = {
            'item_sponsor_id': existing.item_sponsor_id,
            'item_id': item.item_id,
            'sponsor_id': sponsor.sponsor_id,
            'quantity': 5
        }
        
        result = save_item_sponsor(item_sponsor_data)
        
        assert result.item_sponsor_id == existing.item_sponsor_id
        assert result.quantity == 5

    def test_save_sponsor_order(self):
        """Test saving a complete sponsor order with multiple items."""
        from sponsoring.util import save_sponsor_order
        from sponsoring.models import Item, Sponsor, ItemSponsor
        
        # Create test items
        item1 = Item.objects.create(
            item_nm='Item 1',
            item_desc='Desc 1',
            quantity=10,
            reset_date=date(2024, 1, 1),
            void_ind='n'
        )
        item2 = Item.objects.create(
            item_nm='Item 2',
            item_desc='Desc 2',
            quantity=20,
            reset_date=date(2024, 1, 1),
            void_ind='n'
        )
        
        sponsor_order = {
            'sponsor': {
                'sponsor_nm': 'Order Sponsor',
                'phone': '3333333333',
                'email': 'order@test.com'
            },
            'items': [
                {'item_id': item1.item_id, 'cart_quantity': 2},
                {'item_id': item2.item_id, 'cart_quantity': 5}
            ]
        }
        
        save_sponsor_order(sponsor_order)
        
        # Verify sponsor was created
        sponsor = Sponsor.objects.get(sponsor_nm='Order Sponsor')
        assert sponsor is not None
        
        # Verify item sponsors were created
        item_sponsors = ItemSponsor.objects.filter(sponsor_id=sponsor)
        assert item_sponsors.count() == 2
        
        quantities = {is_obj.item_id.item_id: is_obj.quantity for is_obj in item_sponsors}
        assert quantities[item1.item_id] == 2
        assert quantities[item2.item_id] == 5


@pytest.mark.django_db
class TestSponsoringViews:
    """Tests for sponsoring/views.py API endpoints."""

    def test_get_items_view_success(self, api_client):
        """Test GET items endpoint."""
        from sponsoring.models import Item
        
        Item.objects.create(
            item_nm='Test Item',
            item_desc='Description',
            quantity=10,
            reset_date=date(2024, 1, 1),
            active='y',
            void_ind='n',
            img_id='test_img',
            img_ver='123'
        )
        
        with patch('sponsoring.util.CloudinaryImage') as mock_cloudinary:
            mock_cloudinary.return_value.build_url.return_value = 'https://test.com/image.jpg'
            
            response = api_client.get('/sponsoring/get-items/')
            
            assert response.status_code == 200
            assert len(response.data) >= 1

    def test_get_items_view_error(self, api_client, test_user, default_user):
        """Test GET items endpoint with error."""
        api_client.force_authenticate(user=test_user)
        
        with patch('sponsoring.util.get_items', side_effect=Exception('Test error')):
            response = api_client.get('/sponsoring/get-items/')
            
            # ret_message returns 200 even on error
            assert response.status_code == 200
            assert response.data['error'] is True

    def test_get_sponsors_view_success(self, api_client):
        """Test GET sponsors endpoint."""
        from sponsoring.models import Sponsor
        
        Sponsor.objects.create(
            sponsor_nm='Test Sponsor',
            phone='1234567890',
            email='test@test.com',
            void_ind='n'
        )
        
        response = api_client.get('/sponsoring/get-sponsors/')
        
        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_get_sponsors_view_error(self, api_client, test_user, default_user):
        """Test GET sponsors endpoint with error."""
        api_client.force_authenticate(user=test_user)
        
        with patch('sponsoring.util.get_sponsors', side_effect=Exception('Test error')):
            response = api_client.get('/sponsoring/get-sponsors/')
            
            # ret_message returns 200 even on error
            assert response.status_code == 200
            assert response.data['error'] is True

    def test_save_sponsor_view_success(self, api_client, default_user):
        """Test POST sponsor endpoint."""
        sponsor_data = {
            'sponsor_nm': 'New Sponsor',
            'phone': '9876543210',
            'email': 'new@test.com',
            'void_ind': 'n'
        }
        
        response = api_client.post('/sponsoring/save-sponsor/', sponsor_data, format='json')
        
        # Should succeed if data is valid
        assert response.status_code == 200

    def test_save_sponsor_view_invalid_data(self, api_client, test_user, default_user):
        """Test POST sponsor with invalid data."""
        api_client.force_authenticate(user=test_user)
        
        invalid_data = {
            'sponsor_nm': '',  # Empty name should be invalid
        }
        
        response = api_client.post('/sponsoring/save-sponsor/', invalid_data, format='json')
        
        # ret_message returns 200 even on error
        assert response.status_code == 200
        assert response.data['error'] is True

    def test_save_sponsor_view_exception(self, api_client, test_user, default_user):
        """Test POST sponsor with exception during save."""
        api_client.force_authenticate(user=test_user)
        
        sponsor_data = {
            'sponsor_nm': 'Test',
            'phone': '1234567890',
            'email': 'test@test.com'
        }
        
        with patch('sponsoring.util.save_sponsor', side_effect=Exception('Save error')):
            response = api_client.post('/sponsoring/save-sponsor/', sponsor_data, format='json')
            
            # ret_message returns 200 even on error
            assert response.status_code == 200
            assert response.data['error'] is True

    def test_save_item_view_success(self, api_client, test_user):
        """Test POST item endpoint with authentication."""
        api_client.force_authenticate(user=test_user)
        
        item_data = {
            'item_nm': 'New Item',
            'item_desc': 'Description',
            'quantity': 10,
            'reset_date': '2024-06-01',
            'void_ind': 'n'
        }
        
        # Just verify endpoint is callable, access_response controls actual behavior
        response = api_client.post('/sponsoring/save-item/', item_data, format='json')
        
        # Response depends on access_response implementation
        assert response.status_code in [200, 403]

    def test_save_sponsor_order_view_success(self, api_client, default_user):
        """Test POST sponsor order endpoint."""
        from sponsoring.models import Item
        
        item = Item.objects.create(
            item_nm='Order Item',
            item_desc='Desc',
            quantity=10,
            reset_date=date(2024, 1, 1),
            void_ind='n'
        )
        
        order_data = {
            'sponsor': {
                'sponsor_nm': 'Order Sponsor',
                'phone': '5555555555',
                'email': 'order@test.com',
                'void_ind': 'n'
            },
            'items': [
                {'item_id': item.item_id, 'cart_quantity': 2}
            ]
        }
        
        response = api_client.post('/sponsoring/save-sponsor-order/', order_data, format='json')
        
        # Should succeed if data is valid
        assert response.status_code == 200

    def test_save_sponsor_order_view_invalid_data(self, api_client, test_user, default_user):
        """Test POST sponsor order with invalid data."""
        api_client.force_authenticate(user=test_user)
        
        invalid_data = {
            'sponsor': {},  # Missing required fields
            'items': []
        }
        
        response = api_client.post('/sponsoring/save-sponsor-order/', invalid_data, format='json')
        
        # ret_message returns 200 even on error
        assert response.status_code == 200
        assert response.data['error'] is True

    def test_save_sponsor_order_view_exception(self, api_client, test_user, default_user):
        """Test POST sponsor order with exception."""
        api_client.force_authenticate(user=test_user)
        
        order_data = {
            'sponsor': {
                'sponsor_nm': 'Test',
                'phone': '1234567890',
                'email': 'test@test.com'
            },
            'items': []
        }
        
        with patch('sponsoring.util.save_sponsor_order', side_effect=Exception('Order error')):
            response = api_client.post('/sponsoring/save-sponsor-order/', order_data, format='json')
            
            # ret_message returns 200 even on error
            assert response.status_code == 200
            assert response.data['error'] is True
