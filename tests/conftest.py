import os

from unittest import mock
import pytest

pytest_plugins = ["pytester"]


@pytest.fixture
def set_env():
    os.environ["OBJECT_STORAGE_ENDPOINT"] = "enm1n5rid50yi.x.pipedream.net"
    os.environ["OBJECT_STORAGE_BUCKET"] = "test"
    os.environ["OBJECT_STORAGE_USERNAME"] = "admin"
    os.environ["OBJECT_STORAGE_PASSWORD"] = "password"
    yield
    del os.environ["OBJECT_STORAGE_ENDPOINT"]
    del os.environ["OBJECT_STORAGE_BUCKET"]
    del os.environ["OBJECT_STORAGE_USERNAME"]
    del os.environ["OBJECT_STORAGE_PASSWORD"]


@pytest.fixture
def minio():
    with mock.patch("pytest_html_object_storage.minio.Minio") as minio_mock, mock.patch(
        "pytest_html_object_storage.minio.uuid"
    ) as uuid_mock:
        client_mock = mock.MagicMock()
        minio_mock.return_value = client_mock
        yield minio_mock, client_mock, uuid_mock
