from typing import Any
from cloudinary import uploader, CloudinaryImage
from django.db.models import Q, Sum, QuerySet
from django.db.models.functions import Lower

from sponsoring.models import Item, Sponsor, ItemSponsor


def get_items() -> list[dict[str, Any]]:
    """
    Get all active items with their sponsorship information.
    
    Returns:
        List of dictionaries containing item details including:
            - item_id, item_nm, item_desc
            - quantity: Total available quantity
            - sponsor_quantity: Amount purchased by sponsors
            - reset_date: Date when quantities reset
            - active: Whether the item is active
            - img_url: Cloudinary URL for the item image
    """
    items = Item.objects.filter(void_ind='n').order_by(Lower('item_nm'))

    ret = []
    for i in items:
        purchased = i.itemsponsor_set.filter(Q(void_ind='n') & Q(time__gte=i.reset_date)).aggregate(Sum('quantity'))
        purchased = purchased.get('quantity__sum', 0)
        purchased = purchased if purchased is not None else 0
        ret.append({
            'item_id': i.item_id,
            'item_nm': i.item_nm,
            'item_desc': i.item_desc,
            'quantity': i.quantity,
            'sponsor_quantity': purchased,
            'reset_date': i.reset_date,
            'active': i.active,
            'img_url': CloudinaryImage(i.img_id, version=i.img_ver).build_url(secure=True)
        })

    return ret


def get_sponsors() -> QuerySet[Sponsor]:
    """
    Get all active sponsors ordered by name.
    
    Returns:
        QuerySet of Sponsor objects
    """
    sponsors = Sponsor.objects.filter(void_ind='n').order_by(Lower('sponsor_nm'))
    return sponsors


def save_sponsor(sponsor: dict[str, Any]) -> Sponsor:
    """
    Create or update a sponsor record.
    
    Args:
        sponsor: Dictionary containing sponsor data (sponsor_id, sponsor_nm, phone, email)
                If sponsor_id is present, updates existing sponsor; otherwise creates new one
                
    Returns:
        The created or updated Sponsor object
    """
    if sponsor.get('sponsor_id', None) is not None:
        s = Sponsor.objects.get(sponsor_id=sponsor['sponsor_id'])
        s.sponsor_nm = sponsor['sponsor_nm']
        s.phone = sponsor['phone']
        s.email = sponsor['email']
    else:
        s = Sponsor(sponsor_nm=sponsor['sponsor_nm'], phone=sponsor['phone'], email=sponsor['email'], void_ind='n')

    s.save()
    return s


def save_item(item: dict[str, Any]) -> Item:
    """
    Create or update an item record, including image upload if provided.
    
    Args:
        item: Dictionary containing item data (item_id, item_nm, item_desc, quantity, 
              reset_date, and optionally img for image upload)
              If item_id is present, updates existing item; otherwise creates new one
              
    Returns:
        The created or updated Item object
    """
    if item.get('item_id', None) is not None:
        i = Item.objects.get(item_id=item['item_id'])
        i.item_nm = item['item_nm']
        i.item_desc = item['item_desc']
        i.quantity = item['quantity']
        i.reset_date = item['reset_date']
    else:
        i = Item(item_nm=item['item_nm'], item_desc=item['item_desc'], quantity=item['quantity'],
                 reset_date=item['reset_date'], void_ind='n')

    i.save()

    if item.get('img', None) is not None:
        if i.img_id:
            response = uploader.upload(item['img'], public_id=i.img_id)
        else:
            response = uploader.upload(item['img'])

        i.img_id = response['public_id']
        i.img_ver = str(response['version'])
        i.save()

    return i


def save_item_sponsor(item_sponsor: dict[str, Any]) -> ItemSponsor:
    """
    Create or update a link between an item and sponsor with quantity.
    
    Args:
        item_sponsor: Dictionary containing item_sponsor_id (optional), item_id, 
                     sponsor_id, and quantity
                     
    Returns:
        The created or updated ItemSponsor object
    """
    if item_sponsor.get('item_sponsor_id', None) is not None:
        i = ItemSponsor.objects.get(item_sponsor_id=item_sponsor['item_sponsor_id'])
        i.item_id.item_id = item_sponsor['item_id']
        i.sponsor_id.sponsor_id = item_sponsor['sponsor_id']
        i.quantity = item_sponsor['quantity']
    else:
        i = ItemSponsor(item_id_id=item_sponsor['item_id'], sponsor_id_id=item_sponsor['sponsor_id'],
                        quantity=item_sponsor['quantity'], void_ind='n')

    i.save()
    return i


def save_sponsor_order(sponsor_order: dict[str, Any]) -> None:
    """
    Process a complete sponsor order with multiple items.
    
    Args:
        sponsor_order: Dictionary containing:
            - sponsor: Sponsor information dictionary
            - items: List of items with item_id and cart_quantity
    """
    s = save_sponsor(sponsor_order['sponsor'])

    for i in sponsor_order['items']:
        item_sponsor = {
            'item_id': i['item_id'],
            'sponsor_id': s.sponsor_id,
            'quantity': i['cart_quantity']
        }
        save_item_sponsor(item_sponsor)
