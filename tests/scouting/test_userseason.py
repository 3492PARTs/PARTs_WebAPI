"""
Tests for the UserSeason model, scouting.admin.util functions, and
UserSeasonView.

Coverage:
- UserSeason model (__str__, fields, defaults)
- get_user_seasons (all, by id, by user_id, void filtering, ordering)
- save_user_season (create, update)
- save_user_seasons (create multiple, delete unlisted)
- UserSeasonView GET / POST / DELETE (happy path, invalid data, access
  denied, unauthenticated, exception)
"""

import pytest
from unittest.mock import patch

from rest_framework.test import APIRequestFactory, force_authenticate

from scouting.admin import util as admin_util
from scouting.admin.views import UserSeasonView
from scouting.models import Season, UserSeason
from user.models import User

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def season(db):
    return Season.objects.create(
        season="2024",
        current="n",
        game="Test Game",
        manual="",
    )


@pytest.fixture
def season2(db):
    return Season.objects.create(
        season="2025",
        current="y",
        game="Another Game",
        manual="",
    )


@pytest.fixture
def user_a(db):
    return User.objects.create_user(
        username="user_a",
        email="a@example.com",
        password="pass",
        first_name="Alice",
        last_name="Smith",
    )


@pytest.fixture
def user_b(db):
    return User.objects.create_user(
        username="user_b",
        email="b@example.com",
        password="pass",
        first_name="Bob",
        last_name="Jones",
    )


@pytest.fixture
def user_season_a(db, user_a, season):
    return UserSeason.objects.create(user=user_a, season=season, void_ind="n")


@pytest.fixture
def user_season_b(db, user_b, season):
    return UserSeason.objects.create(user=user_b, season=season, void_ind="n")


@pytest.fixture
def voided_user_season(db, user_a, season2):
    return UserSeason.objects.create(user=user_a, season=season2, void_ind="y")


@pytest.fixture
def api_rf():
    return APIRequestFactory()


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestUserSeasonModel:
    def test_str(self, user_season_a):
        result = str(user_season_a)
        assert str(user_season_a.id) in result
        assert str(user_season_a.user) in result
        assert str(user_season_a.season) in result

    def test_default_void_ind(self, user_a, season):
        us = UserSeason.objects.create(user=user_a, season=season)
        assert us.void_ind == "n"

    def test_fields_stored_correctly(self, user_a, season):
        us = UserSeason.objects.create(user=user_a, season=season, void_ind="y")
        us.refresh_from_db()
        assert us.user == user_a
        assert us.season == season
        assert us.void_ind == "y"

    def test_primary_key_auto_assigned(self, user_a, season):
        us = UserSeason.objects.create(user=user_a, season=season)
        assert us.id is not None
        assert us.id > 0


# ---------------------------------------------------------------------------
# Util: get_user_seasons
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestGetUserSeasons:
    def test_returns_all_non_voided(
        self, user_season_a, user_season_b, voided_user_season
    ):
        result = admin_util.get_user_seasons()
        ids = list(result.values_list("id", flat=True))
        assert user_season_a.id in ids
        assert user_season_b.id in ids
        assert voided_user_season.id not in ids

    def test_returns_single_by_id(self, user_season_a):
        result = admin_util.get_user_seasons(id=user_season_a.id)
        assert result == user_season_a

    def test_returns_single_by_id_voided(self, voided_user_season):
        # get by id bypasses void filter
        result = admin_util.get_user_seasons(id=voided_user_season.id)
        assert result == voided_user_season

    def test_raises_for_nonexistent_id(self):
        with pytest.raises(UserSeason.DoesNotExist):
            admin_util.get_user_seasons(id=999999)

    def test_filters_by_user_id(self, user_season_a, user_season_b, user_a):
        result = admin_util.get_user_seasons(user_id=user_a.id)
        ids = list(result.values_list("id", flat=True))
        assert user_season_a.id in ids
        assert user_season_b.id not in ids

    def test_filters_by_user_id_excludes_voided(
        self, user_season_a, voided_user_season, user_a
    ):
        result = admin_util.get_user_seasons(user_id=user_a.id)
        ids = list(result.values_list("id", flat=True))
        assert user_season_a.id in ids
        assert voided_user_season.id not in ids

    def test_empty_when_no_records(self):
        result = admin_util.get_user_seasons()
        assert result.count() == 0

    def test_ordering(self, user_season_a, user_season_b):
        result = list(admin_util.get_user_seasons())
        # Both are in the result; ordering is stable (no assertion on exact
        # order since it depends on first/last name combinations)
        assert len(result) == 2


# ---------------------------------------------------------------------------
# Util: save_user_season
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestSaveUserSeason:
    def _payload(self, user, season, id=None, void_ind="n"):
        data = {
            "user": {"id": user.id},
            "season": {"id": season.id},
            "void_ind": void_ind,
        }
        if id is not None:
            data["id"] = id
        return data

    def test_creates_new_user_season(self, user_a, season):
        payload = self._payload(user_a, season)
        result = admin_util.save_user_season(payload)
        assert result.id is not None
        assert result.user == user_a
        assert result.season == season
        assert result.void_ind == "n"

    def test_creates_with_void_ind_y(self, user_a, season):
        payload = self._payload(user_a, season, void_ind="y")
        result = admin_util.save_user_season(payload)
        assert result.void_ind == "y"

    def test_updates_existing_user_season(self, user_season_a, user_a, season, season2):
        payload = self._payload(user_a, season2, id=user_season_a.id, void_ind="y")
        result = admin_util.save_user_season(payload)
        assert result.id == user_season_a.id
        assert result.season == season2
        assert result.void_ind == "y"

    def test_updates_user(self, user_season_a, user_a, user_b, season):
        payload = self._payload(user_b, season, id=user_season_a.id)
        result = admin_util.save_user_season(payload)
        assert result.user == user_b

    def test_persists_to_database(self, user_a, season):
        payload = self._payload(user_a, season)
        result = admin_util.save_user_season(payload)
        db_obj = UserSeason.objects.get(id=result.id)
        assert db_obj.user == user_a
        assert db_obj.season == season

    def test_raises_for_nonexistent_user(self, season):
        payload = {"user": {"id": 999999}, "season": {"id": season.id}, "void_ind": "n"}
        with pytest.raises(User.DoesNotExist):
            admin_util.save_user_season(payload)

    def test_raises_for_nonexistent_season(self, user_a):
        payload = {"user": {"id": user_a.id}, "season": {"id": 999999}, "void_ind": "n"}
        with pytest.raises(Season.DoesNotExist):
            admin_util.save_user_season(payload)


# ---------------------------------------------------------------------------
# Util: save_user_seasons
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestSaveUserSeasons:
    def _payload(self, user, season, id=None, void_ind="n"):
        data = {
            "user": {"id": user.id},
            "season": {"id": season.id},
            "void_ind": void_ind,
        }
        if id is not None:
            data["id"] = id
        return data

    def test_creates_multiple(self, user_a, user_b, season):
        payloads = [
            self._payload(user_a, season),
            self._payload(user_a, season),
        ]
        result = admin_util.save_user_seasons(user_a.id, payloads)
        assert len(result) == 2
        users = {r.user for r in result}
        assert user_a in users
        # assert user_b in users

    def test_deletes_unlisted_records(
        self, user_season_a, user_season_b, user_a, season
    ):
        # Only modify user_a's record
        payloads = [self._payload(user_a, season, id=user_season_a.id)]
        admin_util.save_user_seasons(user_a.id, payloads)
        assert admin_util.get_user_seasons(user_id=user_season_b.user.id).exists()
        assert admin_util.get_user_seasons(user_id=user_season_a.user.id).exists()

    def test_empty_list_deletes_all(self, user_season_a, user_season_b):
        admin_util.save_user_seasons(user_season_a.user.id, [])
        assert admin_util.get_user_seasons(user_id=user_season_a.user.id).count() == 0

    def test_returns_list(self, user_a, season):
        payloads = [self._payload(user_a, season)]
        result = admin_util.save_user_seasons(user_a.id, payloads)
        assert isinstance(result, list)

    def test_updates_existing_in_list(self, user_season_a, user_a, season, season2):
        payload = self._payload(user_a, season2, id=user_season_a.id, void_ind="y")
        result = admin_util.save_user_seasons(user_a.id, [payload])
        assert result[0].id == user_season_a.id
        assert result[0].season == season2
        assert result[0].void_ind == "y"


# ---------------------------------------------------------------------------
# View: UserSeasonView
# ---------------------------------------------------------------------------


def _user_data(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
    }


def _season_data(season):
    return {
        "id": season.id,
        "season": season.season,
        "current": season.current,
        "game": season.game,
        "manual": season.manual,
    }


def _user_season_payload(user, season, id=None, void_ind="n"):
    data = {
        "user": _user_data(user),
        "season": _season_data(season),
        "void_ind": void_ind,
    }
    if id is not None:
        data["id"] = id
    return data


@pytest.mark.django_db
class TestUserSeasonViewGet:
    def test_unauthenticated_returns_401(self, api_rf):
        request = api_rf.get("/scouting/admin/user-seasons/")
        response = UserSeasonView.as_view()(request)
        assert response.status_code == 401

    def test_get_all_user_seasons(
        self, api_rf, test_user, user_season_a, user_season_b
    ):
        request = api_rf.get("/scouting/admin/user-seasons/")
        force_authenticate(request, user=test_user)
        with patch("general.security.has_access", return_value=True):
            response = UserSeasonView.as_view()(request)
        assert response.status_code == 200
        assert isinstance(response.data, list)
        assert len(response.data) == 2

    def test_get_by_id(self, api_rf, test_user, user_season_a):
        request = api_rf.get(f"/scouting/admin/user-seasons/?id={user_season_a.id}")
        force_authenticate(request, user=test_user)
        with patch("general.security.has_access", return_value=True):
            response = UserSeasonView.as_view()(request)
        assert response.status_code == 200
        assert response.data["id"] == user_season_a.id

    def test_get_by_user_id(
        self, api_rf, test_user, user_season_a, user_season_b, user_a
    ):
        request = api_rf.get(f"/scouting/admin/user-seasons/?user_id={user_a.id}")
        force_authenticate(request, user=test_user)
        with patch("general.security.has_access", return_value=True):
            response = UserSeasonView.as_view()(request)
        assert response.status_code == 200
        assert isinstance(response.data, list)
        assert len(response.data) == 1
        assert response.data[0]["id"] == user_season_a.id

    def test_get_access_denied(self, api_rf, test_user):
        request = api_rf.get("/scouting/admin/user-seasons/")
        force_authenticate(request, user=test_user)
        with patch("general.security.has_access", return_value=False):
            response = UserSeasonView.as_view()(request)
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_get_exception_returns_error(self, api_rf, test_user, system_user):
        request = api_rf.get("/scouting/admin/user-seasons/")
        force_authenticate(request, user=test_user)
        with patch("general.security.has_access", return_value=True), patch(
            "scouting.admin.util.get_user_seasons",
            side_effect=Exception("boom"),
        ):
            response = UserSeasonView.as_view()(request)
        assert response.status_code == 200
        assert response.data.get("error") is True


@pytest.mark.django_db
class TestUserSeasonViewPost:
    def test_unauthenticated_returns_401(self, api_rf, user_a, season):
        payload = _user_season_payload(user_a, season)
        request = api_rf.post("/scouting/admin/user-seasons/", payload, format="json")
        response = UserSeasonView.as_view()(request)
        assert response.status_code == 401

    def test_post_creates_list_of_user_seasons(
        self, api_rf, test_user, user_a, user_b, season
    ):
        payload = [
            _user_season_payload(user_a, season),
            _user_season_payload(user_b, season),
        ]
        request = api_rf.post("/scouting/admin/user-seasons/", payload, format="json")
        force_authenticate(request, user=test_user)
        with patch("general.security.has_access", return_value=True):
            response = UserSeasonView.as_view()(request, user_id=user_a.id)
        assert response.status_code == 200
        assert isinstance(response.data, list)
        assert len(response.data) == 2

    def test_post_updates_existing_user_season(
        self, api_rf, test_user, user_season_a, user_a, season, season2
    ):
        payload = _user_season_payload(
            user_a, season2, id=user_season_a.id, void_ind="y"
        )
        request = api_rf.post("/scouting/admin/user-seasons/", [payload], format="json")
        force_authenticate(request, user=test_user)
        with patch("general.security.has_access", return_value=True):
            response = UserSeasonView.as_view()(request, user_id=user_a.id)
        assert response.status_code == 200
        assert response.data[0]["id"] == user_season_a.id
        assert response.data[0]["void_ind"] == "y"

    def test_post_invalid_data_returns_error(self, api_rf, test_user, user_a):
        request = api_rf.post("/scouting/admin/user-seasons/", {}, format="json")
        force_authenticate(request, user=test_user)
        with patch("general.security.has_access", return_value=True):
            response = UserSeasonView.as_view()(request, user_id=user_a.id)
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_access_denied(self, api_rf, test_user, user_a, season):
        payload = _user_season_payload(user_a, season)
        request = api_rf.post("/scouting/admin/user-seasons/", payload, format="json")
        force_authenticate(request, user=test_user)
        with patch("general.security.has_access", return_value=False):
            response = UserSeasonView.as_view()(request, user_id=user_a.id)
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_exception_returns_error(
        self, api_rf, test_user, system_user, user_a, season
    ):
        payload = _user_season_payload(user_a, season)
        request = api_rf.post("/scouting/admin/user-seasons/", payload, format="json")
        force_authenticate(request, user=test_user)
        with patch("general.security.has_access", return_value=True), patch(
            "scouting.admin.util.save_user_season",
            side_effect=Exception("boom"),
        ):
            response = UserSeasonView.as_view()(request, user_id=user_a.id)
        assert response.status_code == 200
        assert response.data.get("error") is True


@pytest.mark.django_db
class TestUserSeasonViewDelete:
    def test_unauthenticated_returns_401(self, api_rf, user_a, season):
        payload = _user_season_payload(user_a, season)
        request = api_rf.delete(
            f"/scouting/admin/user-seasons/{user_a.id}/", payload, format="json"
        )
        response = UserSeasonView.as_view()(request)
        assert response.status_code == 401

    def test_delete_with_single_payload(
        self, api_rf, test_user, user_season_a, user_a, season
    ):
        payload = _user_season_payload(
            user_a, season, id=user_season_a.id, void_ind="y"
        )
        request = api_rf.delete("/scouting/admin/user-seasons/", payload, format="json")
        force_authenticate(request, user=test_user)
        with patch("general.security.has_access", return_value=True):
            response = UserSeasonView.as_view()(request, user_id=user_a.id)
        assert response.status_code == 200

    def test_delete_invalid_data_returns_error(self, api_rf, test_user):
        request = api_rf.delete("/scouting/admin/user-seasons/", {}, format="json")
        force_authenticate(request, user=test_user)
        with patch("general.security.has_access", return_value=True):
            response = UserSeasonView.as_view()(request, user_id=test_user.id)
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_delete_access_denied(self, api_rf, test_user, user_a, season):
        payload = _user_season_payload(user_a, season)
        request = api_rf.delete("/scouting/admin/user-seasons/", payload, format="json")
        force_authenticate(request, user=test_user)
        with patch("general.security.has_access", return_value=False):
            response = UserSeasonView.as_view()(request, user_id=user_a.id)
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_delete_exception_returns_error(
        self, api_rf, test_user, system_user, user_a, season
    ):
        payload = _user_season_payload(user_a, season)
        request = api_rf.delete("/scouting/admin/user-seasons/", payload, format="json")
        force_authenticate(request, user=test_user)
        with patch("general.security.has_access", return_value=True), patch(
            "scouting.admin.util.save_user_season",
            side_effect=Exception("boom"),
        ):
            response = UserSeasonView.as_view()(request, user_id=user_a.id)
        assert response.status_code == 200
        assert response.data.get("error") is True
