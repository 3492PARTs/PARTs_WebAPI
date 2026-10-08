"""
Comprehensive tests for the resources app.
"""

import pytest
from unittest.mock import patch
from rest_framework.test import force_authenticate


@pytest.mark.django_db
class TestResourcesModels:
    """Tests for resources model methods."""

    @pytest.fixture
    def resource_type(self):
        from resources.models import ResourceType

        return ResourceType.objects.create(
            name="Tools", description="Hand tools", void_ind="n"
        )

    @pytest.fixture
    def resource(self, resource_type):
        from resources.models import Resource

        return Resource.objects.create(
            resource_type=resource_type,
            name="Drill",
            description="Cordless drill",
            void_ind="n",
        )

    def test_resource_type_str(self, resource_type):
        assert str(resource_type) == f"{resource_type.id} : Tools"

    def test_resource_str(self, resource):
        assert str(resource) == f"{resource.id} : Drill"

    def test_resource_not_checked_out_by_default(self, resource):
        assert resource.is_checked_out() is False
        assert resource.checked_out is False

    def test_resource_checked_out_true_when_open_checkout(self, resource, test_user):
        from resources.models import ResourceCheckOut

        ResourceCheckOut.objects.create(resource=resource, user=test_user, void_ind="n")

        assert resource.is_checked_out() is True
        assert resource.checked_out is True

    def test_resource_not_checked_out_when_checked_in(self, resource, test_user):
        from resources.models import ResourceCheckOut
        from django.utils.timezone import now

        ResourceCheckOut.objects.create(
            resource=resource, user=test_user, time_in=now(), void_ind="n"
        )

        assert resource.is_checked_out() is False

    def test_checkout_str_and_is_checked_in(self, resource, test_user):
        from resources.models import ResourceCheckOut

        checkout = ResourceCheckOut.objects.create(
            resource=resource, user=test_user, void_ind="n"
        )
        assert str(checkout) == f"{checkout.id} : {resource} : {test_user}"
        assert checkout.is_checked_in() is False


@pytest.mark.django_db
class TestResourcesUtil:
    """Tests for resources utility functions."""

    @pytest.fixture
    def resource_type(self):
        from resources.models import ResourceType

        return ResourceType.objects.create(
            name="Tools", description="Hand tools", void_ind="n"
        )

    @pytest.fixture
    def resource(self, resource_type):
        from resources.models import Resource

        return Resource.objects.create(
            resource_type=resource_type,
            name="Drill",
            description="Cordless drill",
            void_ind="n",
        )

    # ResourceType util

    def test_get_resource_types_all(self, resource_type):
        from resources.util import get_resource_types

        types = get_resource_types()
        assert len(types) == 1
        assert types[0] == resource_type

    def test_get_resource_types_excludes_void(self, resource_type):
        from resources.models import ResourceType
        from resources.util import get_resource_types

        ResourceType.objects.create(name="Voided", void_ind="y")

        types = get_resource_types()
        assert len(types) == 1

    def test_get_resource_types_by_id(self, resource_type):
        from resources.util import get_resource_types

        result = get_resource_types(resource_type.id)
        assert result == resource_type

    def test_save_resource_type_create(self):
        from resources.util import save_resource_type

        result = save_resource_type({"name": "Electronics", "description": "Wires"})

        assert result.id is not None
        assert result.name == "Electronics"
        assert result.void_ind == "n"

    def test_save_resource_type_update(self, resource_type):
        from resources.util import save_resource_type

        result = save_resource_type(
            {"id": resource_type.id, "name": "Updated Tools", "description": "New desc"}
        )

        assert result.id == resource_type.id
        assert result.name == "Updated Tools"

    def test_delete_resource_type(self, resource_type):
        from resources.util import delete_resource_type

        result = delete_resource_type(resource_type.id)
        assert result.void_ind == "y"

    # Resource util

    def test_get_resources_all(self, resource):
        from resources.util import get_resources

        result = get_resources()
        assert len(result) == 1
        assert result[0] == resource

    def test_get_resources_by_type(self, resource, resource_type):
        from resources.models import ResourceType, Resource
        from resources.util import get_resources

        other_type = ResourceType.objects.create(name="Electronics", void_ind="n")
        Resource.objects.create(
            resource_type=other_type, name="Multimeter", void_ind="n"
        )

        result = get_resources(resource_type_id=resource_type.id)
        assert len(result) == 1
        assert result[0] == resource

    def test_get_resources_by_id(self, resource):
        from resources.util import get_resources

        result = get_resources(resource.id)
        assert result == resource

    def test_get_resources_excludes_void(self, resource_type):
        from resources.models import Resource
        from resources.util import get_resources

        Resource.objects.create(
            resource_type=resource_type, name="Voided", void_ind="y"
        )

        result = get_resources()
        assert len(result) == 0

    def test_save_resource_create(self, resource_type):
        from resources.util import save_resource

        result = save_resource(
            {
                "name": "Hammer",
                "description": "Claw hammer",
                "resource_type": {"id": resource_type.id},
            }
        )

        assert result.id is not None
        assert result.name == "Hammer"
        assert result.resource_type == resource_type

    def test_save_resource_update(self, resource, resource_type):
        from resources.util import save_resource

        result = save_resource(
            {
                "id": resource.id,
                "name": "Updated Drill",
                "description": "Updated desc",
                "resource_type": {"id": resource_type.id},
            }
        )

        assert result.id == resource.id
        assert result.name == "Updated Drill"

    def test_delete_resource(self, resource):
        from resources.util import delete_resource

        result = delete_resource(resource.id)
        assert result.void_ind == "y"

    # Checkout util

    def test_check_out_resource(self, resource, test_user):
        from resources.util import check_out_resource

        checkout = check_out_resource(resource.id, test_user.id)

        assert checkout.id is not None
        assert checkout.resource == resource
        assert checkout.user == test_user
        assert checkout.time_in is None

    def test_check_out_resource_already_checked_out_raises(self, resource, test_user):
        from resources.util import check_out_resource

        check_out_resource(resource.id, test_user.id)

        with pytest.raises(Exception, match="already checked out"):
            check_out_resource(resource.id, test_user.id)

    def test_check_in_resource_by_checkout_id(self, resource, test_user):
        from resources.util import check_out_resource, check_in_resource

        checkout = check_out_resource(resource.id, test_user.id)
        result = check_in_resource(checkout_id=checkout.id)

        assert result.time_in is not None
        assert resource.is_checked_out() is False

    def test_check_in_resource_by_resource_id(self, resource, test_user):
        from resources.util import check_out_resource, check_in_resource

        check_out_resource(resource.id, test_user.id)
        result = check_in_resource(resource_id=resource.id)

        assert result.time_in is not None

    def test_check_in_resource_not_checked_out_raises(self, resource):
        from resources.util import check_in_resource

        with pytest.raises(Exception, match="not currently checked out"):
            check_in_resource(resource_id=resource.id)

    def test_check_in_resource_already_checked_in_raises(self, resource, test_user):
        from resources.util import check_out_resource, check_in_resource

        checkout = check_out_resource(resource.id, test_user.id)
        check_in_resource(checkout_id=checkout.id)

        with pytest.raises(Exception, match="already been checked in"):
            check_in_resource(checkout_id=checkout.id)

    def test_check_in_resource_no_ids_raises(self):
        from resources.util import check_in_resource

        with pytest.raises(Exception, match="Either checkout_id or resource_id"):
            check_in_resource()


@pytest.mark.django_db
class TestResourcesViews:
    """Tests for resources views."""

    @pytest.fixture
    def resource_type(self):
        from resources.models import ResourceType

        return ResourceType.objects.create(
            name="Tools", description="Hand tools", void_ind="n"
        )

    @pytest.fixture
    def resource(self, resource_type):
        from resources.models import Resource

        return Resource.objects.create(
            resource_type=resource_type,
            name="Drill",
            description="Cordless drill",
            void_ind="n",
        )

    @staticmethod
    def _mock_access(mock_access):
        def call_fun(path, user_id, auth_obj, error_msg, fun):
            return fun()

        mock_access.side_effect = call_fun

    def test_resource_types_view_get_all(self, api_rf, test_user, resource_type):
        from resources.views import ResourceTypesView

        with patch("resources.views.access_response") as mock_access:
            self._mock_access(mock_access)

            request = api_rf.get("/resources/resource-types/")
            force_authenticate(request, user=test_user)
            response = ResourceTypesView.as_view()(request)

            assert response.status_code == 200
            assert len(response.data) == 1

    def test_resource_types_view_get_single(self, api_rf, test_user, resource_type):
        from resources.views import ResourceTypesView

        with patch("resources.views.access_response") as mock_access:
            self._mock_access(mock_access)

            request = api_rf.get(
                f"/resources/resource-types/?resource_type_id={resource_type.id}"
            )
            force_authenticate(request, user=test_user)
            response = ResourceTypesView.as_view()(request)

            assert response.status_code == 200
            assert response.data["name"] == "Tools"

    def test_resource_types_view_post_create(self, api_rf, test_user):
        from resources.views import ResourceTypesView

        with patch("resources.views.access_response") as mock_access:
            self._mock_access(mock_access)

            data = {"name": "Electronics", "description": "Wires and boards"}
            request = api_rf.post("/resources/resource-types/", data, format="json")
            force_authenticate(request, user=test_user)
            response = ResourceTypesView.as_view()(request)

            assert response.status_code == 200
            assert response.data["name"] == "Electronics"

    def test_resource_types_view_post_invalid_data(self, api_rf, test_user):
        from resources.views import ResourceTypesView

        with patch("resources.views.access_response") as mock_access:
            self._mock_access(mock_access)

            request = api_rf.post("/resources/resource-types/", {}, format="json")
            force_authenticate(request, user=test_user)
            response = ResourceTypesView.as_view()(request)

            assert response.data["error"] is True

    def test_resource_types_view_delete(self, api_rf, test_user, resource_type):
        from resources.views import ResourceTypesView
        from resources.models import ResourceType

        with patch("resources.views.access_response") as mock_access:
            self._mock_access(mock_access)

            request = api_rf.delete(
                f"/resources/resource-types/?resource_type_id={resource_type.id}"
            )
            force_authenticate(request, user=test_user)
            response = ResourceTypesView.as_view()(request)

            assert response.data["error"] is False
            assert ResourceType.objects.get(id=resource_type.id).void_ind == "y"

    def test_resource_types_view_delete_missing_id(self, api_rf, test_user):
        from resources.views import ResourceTypesView

        with patch("resources.views.access_response") as mock_access:
            self._mock_access(mock_access)

            request = api_rf.delete("/resources/resource-types/")
            force_authenticate(request, user=test_user)
            response = ResourceTypesView.as_view()(request)

            assert response.data["error"] is True

    def test_resources_view_get_all(self, api_rf, test_user, resource):
        from resources.views import ResourcesView

        with patch("resources.views.access_response") as mock_access:
            self._mock_access(mock_access)

            request = api_rf.get("/resources/resources/")
            force_authenticate(request, user=test_user)
            response = ResourcesView.as_view()(request)

            assert response.status_code == 200
            assert len(response.data) == 1

    def test_resources_view_post_create(self, api_rf, test_user, resource_type):
        from resources.views import ResourcesView

        with patch("resources.views.access_response") as mock_access:
            self._mock_access(mock_access)

            data = {
                "name": "Hammer",
                "description": "Claw hammer",
                "resource_type": {"id": resource_type.id, "name": resource_type.name},
            }
            request = api_rf.post("/resources/resources/", data, format="json")
            force_authenticate(request, user=test_user)
            response = ResourcesView.as_view()(request)

            assert response.status_code == 200
            assert response.data["name"] == "Hammer"

    def test_resources_view_delete(self, api_rf, test_user, resource):
        from resources.views import ResourcesView
        from resources.models import Resource

        with patch("resources.views.access_response") as mock_access:
            self._mock_access(mock_access)

            request = api_rf.delete(f"/resources/resources/?resource_id={resource.id}")
            force_authenticate(request, user=test_user)
            response = ResourcesView.as_view()(request)

            assert response.data["error"] is False
            assert Resource.objects.get(id=resource.id).void_ind == "y"

    def test_resource_checkouts_view_get(self, api_rf, test_user, resource):
        from resources.views import ResourceCheckOutsView
        from resources.models import ResourceCheckOut

        ResourceCheckOut.objects.create(resource=resource, user=test_user, void_ind="n")

        with patch("resources.views.access_response") as mock_access:
            self._mock_access(mock_access)

            request = api_rf.get("/resources/resource-checkouts/")
            force_authenticate(request, user=test_user)
            response = ResourceCheckOutsView.as_view()(request)

            assert response.status_code == 200
            assert len(response.data) == 1

    def test_check_out_resource_view(self, api_rf, test_user, resource):
        from resources.views import CheckOutResourceView

        with patch("resources.views.access_response") as mock_access:
            self._mock_access(mock_access)

            data = {"resource_id": resource.id}
            request = api_rf.post("/resources/check-out/", data, format="json")
            force_authenticate(request, user=test_user)
            response = CheckOutResourceView.as_view()(request)

            assert response.status_code == 200
            assert resource.is_checked_out() is True

    def test_check_out_resource_view_invalid_data(self, api_rf, test_user):
        from resources.views import CheckOutResourceView

        with patch("resources.views.access_response") as mock_access:
            self._mock_access(mock_access)

            request = api_rf.post("/resources/check-out/", {}, format="json")
            force_authenticate(request, user=test_user)
            response = CheckOutResourceView.as_view()(request)

            assert response.data["error"] is True

    def test_check_in_resource_view(self, api_rf, test_user, resource):
        from resources.views import CheckOutResourceView, CheckInResourceView

        with patch("resources.views.access_response") as mock_access:
            self._mock_access(mock_access)

            out_request = api_rf.post(
                "/resources/check-out/", {"resource_id": resource.id}, format="json"
            )
            force_authenticate(out_request, user=test_user)
            CheckOutResourceView.as_view()(out_request)

            in_request = api_rf.post(
                "/resources/check-in/", {"resource_id": resource.id}, format="json"
            )
            force_authenticate(in_request, user=test_user)
            response = CheckInResourceView.as_view()(in_request)

            assert response.status_code == 200
            assert resource.is_checked_out() is False
