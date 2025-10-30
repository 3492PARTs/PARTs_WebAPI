import pytest
from unittest.mock import MagicMock, patch

import sponsoring.util as util

class FakeItemSponsorQS(list):
    def aggregate(self, *args, **kwargs):
        return {"quantity__sum": 5}

class FakeItem:
    def __init__(self, item_id=1, item_nm="Name", item_desc="Desc", quantity=10, reset_date=None, active=True, img_id="abc", img_ver="1"):
        self.item_id = item_id
        self.item_nm = item_nm
        self.item_desc = item_desc
        self.quantity = quantity
        self.reset_date = reset_date
        self.active = active
        self.img_id = img_id
        self.img_ver = img_ver
        self.itemsponsor_set = FakeItemSponsorQS()

def test_get_items_builds_cloudinary_url_and_counts(monkeypatch):
    fake_item = FakeItem()
    fake_manager = MagicMock()
    fake_manager.filter.return_value = [fake_item]

    with patch("sponsoring.util.Item") as FakeItemModel, \
         patch("sponsoring.util.cloudinary") as cloudinary:
        FakeItemModel.objects = fake_manager
        ci_instance = MagicMock()
        ci_instance.build_url.return_value = "https://res.cloudinary.com/fake/image.jpg"
        cloudinary.CloudinaryImage.return_value = ci_instance

        items = util.get_items()
        assert isinstance(items, list)
        assert items[0]["item_id"] == fake_item.item_id
        assert items[0]["sponsor_quantity"] == 5
        assert items[0]["img_url"].startswith("https://res.cloudinary.com")

def test_get_sponsors_uses_order(monkeypatch):
    fake_manager = MagicMock()
    fake_manager.filter.return_value = ["s1", "s2"]
    with patch("sponsoring.util.Sponsor") as FakeSponsor:
        FakeSponsor.objects = fake_manager
        sponsors = util.get_sponsors()
        assert sponsors == ["s1", "s2"]
        FakeSponsor.objects.filter.assert_called_once_with(void_ind='n')

def test_save_sponsor_creates_and_updates(monkeypatch):
    saved = {}
    class FakeSponsorModel:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
        def save(self):
            saved["saved_new"] = True

    fake_manager = MagicMock()
    fake_manager.get.side_effect = Exception("not found")
    with patch("sponsoring.util.Sponsor", new=FakeSponsorModel):
        res = util.save_sponsor({"sponsor_nm": "X", "phone": "P", "email": "E"})
        assert saved.get("saved_new", False)

    updated = {}
    class ExistingSponsor:
        sponsor_id = 5
        sponsor_nm = "Old"
        phone = "P"
        email = "E"
        void_ind = "n"
        def save(self):
            updated["saved_update"] = True

    fake_manager2 = MagicMock()
    fake_manager2.get.return_value = ExistingSponsor()
    with patch("sponsoring.util.Sponsor") as FakeSponsor:
        FakeSponsor.objects = fake_manager2
        res = util.save_sponsor({"sponsor_id": 5, "sponsor_nm": "New", "phone": "123", "email": "a@b.com"})
        fake_manager2.get.assert_called_once_with(sponsor_id=5)

def test_save_item_uploads_image_and_updates(monkeypatch):
    created = {}
    class FakeItemModel:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
            self.img_id = None
            self.img_ver = None
        def save(self):
            created["saved"] = True

    fake_manager = MagicMock()
    fake_manager.get.side_effect = Exception("not found")
    with patch("sponsoring.util.Item", new=FakeItemModel), \
         patch("sponsoring.util.Item.objects", new=fake_manager), \
         patch("sponsoring.util.cloudinary.uploader") as uploader:
        uploader.upload.return_value = {"public_id": "pid", "version": 42}
        item = util.save_item({"item_nm": "i", "item_desc": "d", "quantity": 1, "reset_date": None, "img": b"image-bytes"})
        assert created.get("saved", False)
        assert item.img_id == "pid"
        assert item.img_ver == "42"

def test_save_item_sponsor_create_and_update(monkeypatch):
    created = {}
    class FakeItemSponsor:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
        def save(self):
            created["saved"] = True

    fake_manager = MagicMock()
    fake_manager.get.side_effect = Exception("not found")
    with patch("sponsoring.util.ItemSponsor", new=FakeItemSponsor), \
         patch("sponsoring.util.ItemSponsor.objects", new=fake_manager):
        res = util.save_item_sponsor({"item_id": 1, "sponsor_id": 2, "quantity": 3})
        assert created.get("saved", False)

def test_save_item_uploads_image_and_updates(monkeypatch):
    created = {}
    class FakeItemModel:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
            self.img_id = None
            self.img_ver = None
        def save(self):
            created["saved"] = True

    fake_manager = MagicMock()
    fake_manager.get.side_effect = Exception("not found")
    with patch("sponsoring.util.Item", new=FakeItemModel), \
         patch("sponsoring.util.Item.objects", new=fake_manager), \
         patch("sponsoring.util.cloudinary.uploader") as uploader:
        uploader.upload.return_value = {"public_id": "pid", "version": 42}
        item = util.save_item({"item_nm": "i", "item_desc": "d", "quantity": 1, "reset_date": None, "img": b"image-bytes"})
        assert created.get("saved", False)
        assert item.img_id == "pid"
        assert item.img_ver == "42"


def test_save_item_sponsor_create_and_update(monkeypatch):
    created = {}
    class FakeItemSponsor:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
        def save(self):
            created["saved"] = True

    fake_manager = MagicMock()
    fake_manager.get.side_effect = Exception("not found")
    with patch("sponsoring.util.ItemSponsor", new=FakeItemSponsor), \
         patch("sponsoring.util.ItemSponsor.objects", new=fake_manager):
        res = util.save_item_sponsor({"item_id": 1, "sponsor_id": 2, "quantity": 3})
        assert created.get("saved", False)
