import traceback
from typing import Callable, Any
from django.utils import timezone
from django.db.models import QuerySet
from django.contrib.auth.models import Group

import json
from admin.models import ErrorLog
from user.serializers import RetMessageSerializer
from rest_framework.response import Response
from user.models import User, Permission


def has_access(user_id: int, sec_permission: str | list[str]) -> bool:
    """
    Check if a user has the specified permission(s).
    
    Args:
        user_id: The ID of the user to check permissions for
        sec_permission: A single permission codename or list of permission codenames
        
    Returns:
        True if the user has at least one of the specified permissions, False otherwise
        
    Example:
        has_access(request.user.id, 'admin')
        has_access(request.user.id, ['admin', 'scoutadmin'])
    """
    prmsns = get_user_permissions(user_id, False)

    if not isinstance(sec_permission, list):
        sec_permission = [sec_permission]

    prmsn = prmsns.filter(codename__in=sec_permission)

    return len(prmsn) > 0


def access_response(
    endpoint: str, 
    user_id: int, 
    sec_permission: str | list[str], 
    error_message: str, 
    fun: Callable[[], Response]
) -> Response:
    """
    Execute a function if user has access, otherwise return an error response.
    
    Args:
        endpoint: The API endpoint path for error logging
        user_id: The ID of the user attempting access
        sec_permission: Required permission(s) - single string or list of strings
        error_message: Error message to display if function execution fails
        fun: The function to execute if user has access
        
    Returns:
        Response from the function if successful, or error response if access denied or exception occurs
    """
    if has_access(user_id, sec_permission):
        try:
            return fun()
        except Exception as e:
            return ret_message(
                error_message,
                True,
                endpoint,
                -1,
                e,
            )
    else:
        return ret_message(
            "You do not have access.",
            True,
            endpoint,
            user_id,
        )


def get_user_permissions(user_id: int, as_list: bool = True) -> list[Permission] | QuerySet[Permission]:
    """
    Get all permissions for a user based on their group memberships.
    
    Args:
        user_id: The ID of the user
        as_list: If True, return a list of Permission objects. If False, return a QuerySet
        
    Returns:
        List of Permission objects if as_list is True, otherwise a Permission QuerySet
    """
    permissions_queryset = Permission.objects.filter(
        group__user=User.objects.get(id=user_id)
    ).distinct()

    if not as_list:
        return permissions_queryset
    else:
        prmsns = []
        for prmsn in permissions_queryset:
            prmsns.append(prmsn)
        return prmsns


def get_user_groups(user_id: int) -> QuerySet[Group]:
    """
    Get all groups that a user belongs to.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        QuerySet of Group objects the user belongs to
    """
    user = User.objects.get(id=user_id)

    augs = user.groups.all()

    return augs


def ret_message(
    message: str, 
    error: bool = False, 
    path: str = "", 
    user_id: int = -1, 
    exception: Exception | None = None, 
    error_message: str | dict | None = None
) -> Response:
    """
    Create a standardized response message and log errors if applicable.
    
    This function is the standard way to return responses from API endpoints.
    When error=True, it logs the error to the database and prints debug information.
    
    Args:
        message: The message to return to the user
        error: Whether this is an error response
        path: The API endpoint path where the error occurred
        user_id: The ID of the user who triggered the error
        exception: The exception object if an exception occurred
        error_message: Additional error details (typically validation errors or messages)
        
    Returns:
        Response object with the message, error flag, and error details
    """
    # TODO Make all of these optional in the DB
    if error:
        print("----------ERROR START----------")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            user = User.objects.get(id=-1)
            err_msg = "Ran into DoesNotExist exception finding user"
            print(err_msg)
            message += f"\n{err_msg}\n"

        tb = traceback.format_exc()

        tb = (tb[:4000] + "..") if len(tb) > 4000 else tb

        print("Error in: " + path)
        print("Message: " + message)
        print(
            "Error by: " + user.username + " " + user.first_name + " " + user.last_name
        )
        print("Exception: ")
        print(exception)

        print("TraceBack: ")
        print(tb)

        print("----------ERROR END----------")

        try:
            ErrorLog(
                user=user,
                path=path,
                message=message[:1000],
                exception=str(exception)[:4000],
                traceback=str(tb)[:4000],
                error_message=(
                    error_message[:4000] if error_message is not None else None
                ),
                time=timezone.now(),
                void_ind="n",
            ).save()
        except Exception as e:
            try:
                ErrorLog(
                    user=User.objects.get(id=-1),
                    path="general.security.ret_message",
                    message=f"Error logging error:\n{message}",
                    exception=str(e)[:4000],
                    time=timezone.now(),
                    void_ind="n",
                ).save()
            except Exception as e:
                message += "\nCritical Error: please email the team admin at team3492@gmail.com\nSend them this message:\n"
                message += str(e)
                print("The most fatal of errors nothing was logged in db")
                print("Exception: ")
                print(e)

            return Response(
                RetMessageSerializer(
                    {
                        "retMessage": message,
                        "error": error,
                        "errorMessage": (
                            json.dumps(error_message)
                            if error_message is not None
                            else ""
                        ),
                    }
                ).data
            )
    return Response(
        RetMessageSerializer(
            {
                "retMessage": message,
                "error": error,
                "errorMessage": (
                    json.dumps(error_message) if error_message is not None else ""
                ),
            }
        ).data
    )
