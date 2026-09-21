from typing import Any
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, QuerySet
from django.utils.timezone import now as timezone_now

from resources.models import Resource, ResourceType, ResourceCheckOut
from user.models import User


def get_resource_types(id: int = None) -> QuerySet[ResourceType] | ResourceType:
    """
    Get resource types.

    Args:
        id: Optional resource type ID. If provided, returns a single ResourceType.

    Returns:
        QuerySet of non-voided ResourceType objects, or a single ResourceType if id is provided.
    """
    if id is not None:
        return ResourceType.objects.get(id=id)

    return ResourceType.objects.filter(void_ind="n").order_by("name")


def save_resource_type(resource_type: dict[str, Any]) -> ResourceType:
    """
    Create or update a resource type.

    Args:
        resource_type: Dictionary containing resource type data (id, name, description, void_ind).
                       If id is present, updates existing resource type; otherwise creates new one.

    Returns:
        The created or updated ResourceType object.
    """
    if resource_type.get("id", None) is not None:
        rt = ResourceType.objects.get(id=resource_type["id"])
    else:
        rt = ResourceType()

    rt.name = resource_type["name"]
    rt.description = resource_type.get("description", None)
    rt.void_ind = resource_type.get("void_ind", "n")

    rt.save()
    return rt


def delete_resource_type(id: int) -> ResourceType:
    """
    Soft delete a resource type by setting void_ind to 'y'.

    Args:
        id: The ID of the resource type to delete.

    Returns:
        The voided ResourceType object.
    """
    rt = ResourceType.objects.get(id=id)
    rt.void_ind = "y"
    rt.save()
    return rt


def get_resources(
    id: int = None, resource_type_id: int = None
) -> QuerySet[Resource] | Resource:
    """
    Get resources, optionally filtered by resource type.

    Args:
        id: Optional resource ID. If provided, returns a single Resource.
        resource_type_id: Optional resource type ID to filter by.

    Returns:
        QuerySet of non-voided Resource objects, or a single Resource if id is provided.
    """
    if id is not None:
        return Resource.objects.get(id=id)

    cond = Q()
    if resource_type_id is not None:
        cond = Q(resource_type_id=resource_type_id)

    return Resource.objects.filter(cond & Q(void_ind="n")).order_by("name")


def save_resource(resource: dict[str, Any]) -> Resource:
    """
    Create or update a resource.

    Args:
        resource: Dictionary containing resource data (id, name, description, resource_type, void_ind).
                  If id is present, updates existing resource; otherwise creates new one.

    Returns:
        The created or updated Resource object.
    """
    if resource.get("id", None) is not None:
        r = Resource.objects.get(id=resource["id"])
    else:
        r = Resource()

    r.name = resource["name"]
    r.description = resource.get("description", None)
    r.resource_type = ResourceType.objects.get(id=resource["resource_type"]["id"])
    r.void_ind = resource.get("void_ind", "n")

    r.save()
    return r


def delete_resource(id: int) -> Resource:
    """
    Soft delete a resource by setting void_ind to 'y'.

    Args:
        id: The ID of the resource to delete.

    Returns:
        The voided Resource object.
    """
    r = Resource.objects.get(id=id)
    r.void_ind = "y"
    r.save()
    return r


def get_checkouts(
    id: int = None,
    resource_id: int = None,
    user_id: int = None,
    active_only: bool = False,
) -> QuerySet[ResourceCheckOut] | ResourceCheckOut:
    """
    Get resource checkout records, optionally filtered by resource, user, or active status.

    Args:
        id: Optional checkout ID. If provided, returns a single ResourceCheckOut.
        resource_id: Optional resource ID to filter by.
        user_id: Optional user ID to filter by.
        active_only: If True, only returns checkouts that have not been checked back in.

    Returns:
        QuerySet of non-voided ResourceCheckOut objects, or a single ResourceCheckOut if id is provided.
    """
    if id is not None:
        return ResourceCheckOut.objects.get(id=id)

    cond = Q()
    if resource_id is not None:
        cond &= Q(resource_id=resource_id)
    if user_id is not None:
        cond &= Q(user_id=user_id)
    if active_only:
        cond &= Q(time_in__isnull=True)

    return ResourceCheckOut.objects.filter(cond & Q(void_ind="n")).order_by("-time_out")


def check_out_resource(resource_id: int, user_id: int) -> ResourceCheckOut:
    """
    Check out a resource to a user.

    Args:
        resource_id: The ID of the resource being checked out.
        user_id: The ID of the user checking out the resource.

    Returns:
        The created ResourceCheckOut object.

    Raises:
        Exception: If the resource is already checked out to someone.
    """
    resource = Resource.objects.get(id=resource_id, void_ind="n")

    if resource.is_checked_out():
        raise Exception("This resource is already checked out.")

    checkout = ResourceCheckOut()
    checkout.resource = resource
    checkout.user = User.objects.get(id=user_id)
    checkout.time_out = timezone_now()
    checkout.save()
    return checkout


def check_in_resource(
    checkout_id: int = None, resource_id: int = None
) -> ResourceCheckOut:
    """
    Check in a previously checked out resource.

    Args:
        checkout_id: The ID of the checkout record to check in.
        resource_id: The ID of the resource to check in (uses the currently open checkout).

    Returns:
        The updated ResourceCheckOut object.

    Raises:
        Exception: If no open checkout is found, or neither checkout_id nor resource_id is provided.
    """
    if checkout_id is not None:
        checkout = ResourceCheckOut.objects.get(id=checkout_id, void_ind="n")
    elif resource_id is not None:
        try:
            checkout = ResourceCheckOut.objects.get(
                resource_id=resource_id, time_in__isnull=True, void_ind="n"
            )
        except ObjectDoesNotExist:
            raise Exception("This resource is not currently checked out.")
    else:
        raise Exception("Either checkout_id or resource_id must be provided.")

    if checkout.time_in is not None:
        raise Exception("This checkout has already been checked in.")

    checkout.time_in = timezone_now()
    checkout.save()
    return checkout
