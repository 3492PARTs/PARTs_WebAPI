from django.db.models import Q
from django.db.models.functions import Lower

from sponsoring.models import Item, Sponsor, ItemSponsor


def get_items():
    items = Item.objects.filter(void_ind='n').order_by(Lower('item_nm'))

    ret = []
    for i in items:
        ret.push({
            'item_id': i.item_id,
            'item_nm': i.item_nm,
            'item_desc': i.item_desc,
            'quantity': i.quantity
        })

    return items


def get_sponsors():
    sponsors = Sponsor.objects.filter(void_ind='n').order_by(Lower('sponsor_nm'))
    return sponsors


def save_sponsor(sponsor):
    if sponsor.get('sponsor_id', None) is not None:
        s = Sponsor.objects.get(sponsor_id=sponsor['sponsor_id'])
        s.sponsor_nm = sponsor['sponsor_nm']
        s.phone = sponsor['phone']
        s.email = sponsor['email']
    else:
        s = Sponsor(sponsor_nm=sponsor['sponsor_nm'], phone=sponsor['phone'], email=sponsor['email'], void_ind='n')

    s.save()


def save_item(item):
    if item.get('item_id', None) is not None:
        i = Item.objects.get(item_id=item['item_id'])
        i.item_nm = item['item_nm']
        i.item_desc = item['item_desc']
        i.quantity = item['quantity']
    else:
        i = Item(item_nm=item['item_nm'], item_desc=item['item_desc'], quantity=item['quantity'], void_ind='n')

    i.save()


def save_item_sponsor(item_sponsor):
    if item_sponsor.get('item_sponsor_id', None) is not None:
        i = ItemSponsor.objects.get(item_sponsor_id=item_sponsor['item_sponsor_id'])
        i.item_id.item_id = item_sponsor['item_id']
        i.sponsor_id.sponsor_id = item_sponsor['sponsor_id']
        i.quantity = item_sponsor['quantity']
    else:
        i = Item(item_id__item_id=item_sponsor['item_id'], sponsor_id__sponsor_id=item_sponsor['sponsor_id'],
                 quantity=item_sponsor['quantity'], void_ind='n')

    i.save()
