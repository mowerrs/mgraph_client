import json
from typing import Any, Callable
import pytest

from mgraph_client import MgraphClient

# from mgraph_client import drives

from mgraph_client import sites as s


@pytest.fixture
def sites(client: MgraphClient) -> s.Sites:
    return client.sites


@pytest.fixture
def site_by_id(sites) -> s.SiteById:
    return sites.by_id("12345")


@pytest.fixture
def site_root(sites) -> s.Sites.Root:
    return sites.root


@pytest.fixture
def site_root_by_relative_path(site_root) -> s.SiteByRelativePath:
    return site_root.by_relative_path("sites/testpath12345")


def test_sites(sites: s.Sites, url: str, check_request_attributes: Callable):
    assert sites.url == f"{url}/sites"

    check_request_attributes(sites, _type="method", GET=True)
    check_request_attributes(sites, _type="query_param", SELECT=True, SEARCH=True)


def test_site_root(
    site_root: s.Sites.Root, url: str, check_request_attributes: Callable
):
    assert site_root.url == f"{url}/sites/root"

    check_request_attributes(site_root, _type="method", GET=True)
    check_request_attributes(site_root, _type="query_param", SELECT=True)


def test_site_by_relative_path(
    site_root_by_relative_path: s.SiteByRelativePath,
    url: str,
    check_request_attributes: Callable,
):
    assert site_root_by_relative_path.url == f"{url}/sites/root:/sites/testpath12345"

    check_request_attributes(site_root_by_relative_path, _type="method", GET=True)
    check_request_attributes(
        site_root_by_relative_path, _type="query_param", SELECT=True
    )


def test_site_by_relative_path_default_drive(
    site_root_by_relative_path: s.SiteByRelativePath,
    url: str,
    check_request_attributes: Callable,
):
    obj = site_root_by_relative_path.drive
    assert obj.url == f"{url}/sites/root:/sites/testpath12345:/drive"

    check_request_attributes(obj, _type="method", GET=True)
    check_request_attributes(obj, _type="query_param", SELECT=True)


def test_site_by_relative_default_drive_root_item(
    site_root_by_relative_path: s.SiteByRelativePath,
    url: str,
    check_request_attributes: Callable,
):
    obj = site_root_by_relative_path.drive.root
    assert obj.url == f"{url}/sites/root:/sites/testpath12345:/drive/root"

    check_request_attributes(obj, _type="method", GET=True)
    check_request_attributes(obj, _type="query_param", SELECT=True, SEARCH=True)


def test_site_by_relative_default_drive_root_item_children(
    site_root_by_relative_path: s.SiteByRelativePath,
    url: str,
    check_request_attributes: Callable,
):
    obj = site_root_by_relative_path.drive.root.children
    assert obj.url == f"{url}/sites/root:/sites/testpath12345:/drive/root/children"

    check_request_attributes(obj, _type="method", GET=True)
    check_request_attributes(
        obj, _type="query_param", SELECT=True, ORDERBY=True, TOP=True
    )


def test_site_by_relative_default_drive_root_item_by_relative_path(
    site_root_by_relative_path: s.SiteByRelativePath,
    url: str,
    check_request_attributes: Callable,
):

    obj = site_root_by_relative_path.drive.root.by_relative_path("secret/files")
    assert obj.url == f"{url}/sites/root:/sites/testpath12345:/drive/root:/secret/files"

    check_request_attributes(obj, _type="method", GET=True)
    check_request_attributes(obj, _type="query_param", SELECT=True, SEARCH=True)


def test_site_by_relative_default_drive_root_item_by_path_relative_children(
    site_root_by_relative_path: s.SiteByRelativePath,
    url: str,
    check_request_attributes: Callable,
):
    obj = site_root_by_relative_path.drive.root.by_relative_path(
        "secret/files"
    ).children

    assert (
        obj.url
        == f"{url}/sites/root:/sites/testpath12345:/drive/root:/secret/files:/children"
    )

    check_request_attributes(obj, _type="method", GET=True)
    check_request_attributes(
        obj,
        _type="query_param",
        SELECT=True,
        ORDERBY=True,
        TOP=True,
    )


def test_site_by_id(
    site_by_id: s.SiteById, url: str, check_request_attributes: Callable
):
    assert site_by_id.url == f"{url}/sites/12345"

    check_request_attributes(site_by_id, _type="method", GET=True)
    check_request_attributes(site_by_id, _type="query_param", SELECT=True)


def test_site_by_id_default_drive(
    site_by_id: s.SiteById,
    url: str,
    check_request_attributes: Callable,
):
    obj = site_by_id.drive
    assert obj.url == f"{url}/sites/12345/drive"

    check_request_attributes(obj, _type="method", GET=True)
    check_request_attributes(obj, _type="query_param", SELECT=True)


def test_site_by_id_default_drive_root_item(
    site_by_id: s.SiteById,
    url: str,
    check_request_attributes: Callable,
):
    obj = site_by_id.drive.root
    assert obj.url == f"{url}/sites/12345/drive/root"

    check_request_attributes(obj, _type="method", GET=True)
    check_request_attributes(obj, _type="query_param", SELECT=True, SEARCH=True)


def test_site_by_id_default_drive_root_item_children(
    site_by_id: s.SiteById,
    url: str,
    check_request_attributes: Callable,
):
    obj = site_by_id.drive.root.children
    assert obj.url == f"{url}/sites/12345/drive/root/children"

    check_request_attributes(obj, _type="method", GET=True)
    check_request_attributes(
        obj, _type="query_param", SELECT=True, ORDERBY=True, TOP=True
    )


def test_site_by_id_default_drive_root_item_by_relative_path(
    site_by_id: s.SiteById,
    url: str,
    check_request_attributes: Callable,
):
    obj = site_by_id.drive.root.by_relative_path("test_folder/file.csv")
    assert obj.url == f"{url}/sites/12345/drive/root:/test_folder/file.csv"

    check_request_attributes(obj, _type="method", GET=True)
    check_request_attributes(obj, _type="query_param", SELECT=True, SEARCH=True)


def test_site_by_id_default_drive_root_item_by_relative_path_children(
    site_by_id: s.SiteById,
    url: str,
    check_request_attributes: Callable,
):
    obj = site_by_id.drive.root.by_relative_path("test_folder/test_folder1").children
    assert (
        obj.url == f"{url}/sites/12345/drive/root:/test_folder/test_folder1:/children"
    )

    check_request_attributes(obj, _type="method", GET=True)
    check_request_attributes(
        obj, _type="query_param", SELECT=True, ORDERBY=True, TOP=True
    )
