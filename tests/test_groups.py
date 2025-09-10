import json
from typing import Any, Callable
import pytest
from requests import check_compatibility

from mgraph_client.groups import Groups


@pytest.fixture
def groups(client) -> Groups:
    return client.groups


def test_groups(groups: Groups, url: str, check_request_attributes: Callable):
    assert groups.url == f"{url}/groups"
    check_request_attributes(groups, _type="method", GET=True)
    check_request_attributes(
        groups,
        _type="query_param",
        SELECT=True,
        ORDERBY=True,
        FILTER=True,
        TOP=True,
        SEARCH=True,
        COUNT=True,
    )


def test_group(groups: Groups, url: str, check_request_attributes: Callable):
    obj = groups.by_id("12345")
    assert obj.url == f"{url}/groups/12345"
    check_request_attributes(obj, _type="method", GET=True)
    check_request_attributes(obj, _type="query_param", SELECT=True)


def test_group_members(groups: Groups, url: str, check_request_attributes: Callable):
    obj = groups.by_id("12345").members
    assert obj.url == f"{url}/groups/12345/members"
    check_request_attributes(obj, _type="method", GET=True)
    check_request_attributes(
        obj, _type="query_param", SELECT=True, FILTER=True, ORDERBY=True
    )


def test_group_members_ref(
    groups: Groups, url: str, check_request_attributes: Callable
):
    obj = groups.by_id("12345").members.ref
    assert obj.url == f"{url}/groups/12345/members/$ref"
    check_request_attributes(obj, _type="method", POST=True)
    check_request_attributes(obj, _type="query_param")
