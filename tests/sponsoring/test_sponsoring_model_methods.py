"""
Comprehensive tests for Sponsoring model methods to increase coverage.
"""
import pytest
from django.utils import timezone


@pytest.mark.django_db
class TestSponsoringModelStringMethods:
    """Test __str__ methods for sponsoring app models."""
    
    def test_item_str(self):
        """Test Item __str__ method."""
        from sponsoring.models import Item
        
        item = Item.objects.create(
            item_nm="T-Shirt",
            item_desc="Team t-shirt",
            quantity=100
        )
        
        str_result = str(item)
        assert str(item.item_id) in str_result
        assert "T-Shirt" in str_result
    
    def test_sponsor_str(self):
        """Test Sponsor __str__ method."""
        from sponsoring.models import Sponsor
        
        sponsor = Sponsor.objects.create(
            sponsor_nm="Tech Corp",
            phone="555-1234",
            email="contact@techcorp.com"
        )
        
        str_result = str(sponsor)
        assert str(sponsor.sponsor_id) in str_result
        assert "Tech Corp" in str_result
    
    def test_item_sponsor_str(self):
        """Test ItemSponsor __str__ method."""
        from sponsoring.models import Item, Sponsor, ItemSponsor
        
        item = Item.objects.create(
            item_nm="Banner",
            item_desc="Team banner",
            quantity=10
        )
        
        sponsor = Sponsor.objects.create(
            sponsor_nm="Local Business",
            phone="555-5678",
            email="info@local.com"
        )
        
        item_sponsor = ItemSponsor.objects.create(
            item_id=item,
            sponsor_id=sponsor,
            quantity=5
        )
        
        str_result = str(item_sponsor)
        assert str(item_sponsor.item_sponsor_id) in str_result
        assert "5" in str_result


@pytest.mark.django_db
class TestSponsoringModelFields:
    """Test sponsoring model field behaviors."""
    
    def test_item_defaults(self):
        """Test Item default values."""
        from sponsoring.models import Item
        
        item = Item.objects.create(
            item_nm="Widget",
            item_desc="A test widget",
            quantity=50
        )
        
        assert item.active == "y"
        assert item.void_ind == "n"
        assert item.reset_date is not None
        assert item.img_id is None
        assert item.img_ver is None
    
    def test_sponsor_defaults(self):
        """Test Sponsor default values."""
        from sponsoring.models import Sponsor
        
        sponsor = Sponsor.objects.create(
            sponsor_nm="New Sponsor",
            phone="555-9999",
            email="new@sponsor.com"
        )
        
        assert sponsor.can_send_emails is False
        assert sponsor.void_ind == "n"
    
    def test_sponsor_can_send_emails_flag(self):
        """Test Sponsor can_send_emails flag."""
        from sponsoring.models import Sponsor
        
        sponsor = Sponsor.objects.create(
            sponsor_nm="Email Sponsor",
            phone="555-1111",
            email="email@sponsor.com",
            can_send_emails=True
        )
        
        assert sponsor.can_send_emails is True
    
    def test_item_sponsor_defaults(self):
        """Test ItemSponsor default values."""
        from sponsoring.models import Item, Sponsor, ItemSponsor
        
        item = Item.objects.create(
            item_nm="Gadget",
            item_desc="A test gadget",
            quantity=25
        )
        
        sponsor = Sponsor.objects.create(
            sponsor_nm="Sponsor Inc",
            phone="555-2222",
            email="sponsor@inc.com"
        )
        
        item_sponsor = ItemSponsor.objects.create(
            item_id=item,
            sponsor_id=sponsor,
            quantity=10
        )
        
        assert item_sponsor.void_ind == "n"
        assert item_sponsor.time is not None
    
    def test_item_active_flag(self):
        """Test Item active flag can be set."""
        from sponsoring.models import Item
        
        item = Item.objects.create(
            item_nm="Inactive Item",
            item_desc="An inactive item",
            quantity=0,
            active="n"
        )
        
        assert item.active == "n"
    
    def test_item_with_images(self):
        """Test Item with image fields set."""
        from sponsoring.models import Item
        
        item = Item.objects.create(
            item_nm="Item with Image",
            item_desc="Has an image",
            quantity=15,
            img_id="image123",
            img_ver="v1"
        )
        
        assert item.img_id == "image123"
        assert item.img_ver == "v1"
