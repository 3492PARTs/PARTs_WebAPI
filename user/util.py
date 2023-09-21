from django.db.models import Q, ExpressionWrapper, DurationField, F
from django.db.models.functions import Lower

from user.models import User


def get_users(active=True):
    users = User.objects.filter(Q(date_joined__isnull=False)).order_by('-is_active', Lower('first_name'), Lower('last_name'))

    if active:
        users.filter(Q(is_active=True))

    return users
