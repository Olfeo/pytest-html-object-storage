from _pytest.config import ExitCode
from _pytest.pytester import RunResult

import pytest

from unittest import mock


def run(pytester, *args):
    return pytester.runpytest_inprocess("--store-minio", *args)


class TestMinio:
    @pytest.mark.parametrize(
        "pytest_html_args", [None, "--html=test.html", "--self-contained-html"]
    )
    def test_no_pytest_html_params(self, pytester, pytest_html_args):
        pytester.makepyfile(
            """
            def test_pass():
              pass
        """
        )
        result: RunResult = run(pytester, pytest_html_args)
        assert result.ret == ExitCode.INTERNAL_ERROR
        result.stderr.re_match_lines([".*--html.*--self-contained-html.*"])

    def test_nominal(self, pytester, set_env, minio):
        minio_mock, client_mock, uuid_mock = minio

        uuid_mock.uuid4.return_value = "anuuid"
        client_mock.bucket_exists.return_value = True
        pytester.makepyfile(
            """
            def test_pass():
              pass
        """
        )
        result: RunResult = run(
            pytester, "--html=test_report.html", "--self-contained-html"
        )
        assert result.ret == 0
        minio_mock.assert_has_calls(
            [
                mock.call(
                    "enm1n5rid50yi.x.pipedream.net",
                    "admin",
                    "password",
                    region=None,
                    secure=True,
                ),
                mock.call().bucket_exists("test"),
                mock.call().fput_object(
                    "test",
                    "anuuid/report.html",
                    "test_report.html",
                    content_type="text/html",
                ),
            ]
        )
        result.stdout.re_match_lines(
            [
                ".*HTML report sent on MinIO object storage at https://enm1n5rid50yi.x.pipedream.net/test/anuuid/report.html.*"
            ]
        )

    def test_create_bucket(self, pytester, set_env, minio):
        minio_mock, client_mock, uuid_mock = minio

        uuid_mock.uuid4.return_value = "anuuid"
        client_mock.bucket_exists.return_value = False
        pytester.makepyfile(
            """
            def test_pass():
              pass
        """
        )
        result: RunResult = run(
            pytester, "--html=test_report.html", "--self-contained-html"
        )
        assert result.ret == 0
        minio_mock.assert_has_calls(
            [
                mock.call(
                    "enm1n5rid50yi.x.pipedream.net",
                    "admin",
                    "password",
                    region=None,
                    secure=True,
                ),
                mock.call().bucket_exists("test"),
                mock.call().make_bucket("test"),
                mock.call().set_bucket_policy(
                    "test",
                    """{"Version": "2012-10-17", "Id": "testPolicy", "Statement": [{"Sid": "Grant List and GET to everyone", "Effect": "Allow", "Principal": "*", "Action": ["s3:ListBucket", "s3:GetObject"], "Resource": ["test", "test/*"]}]}""",
                ),
                mock.call().fput_object(
                    "test",
                    "anuuid/report.html",
                    "test_report.html",
                    content_type="text/html",
                ),
            ]
        )
        result.stdout.re_match_lines(
            [
                ".*HTML report sent on MinIO object storage at https://enm1n5rid50yi.x.pipedream.net/test/anuuid/report.html.*"
            ]
        )

    def test_no_config(self, pytester):
        pytester.makepyfile("def test_no_config(): pass")
        result: RunResult = run(pytester)
        assert result.ret == ExitCode.INTERNAL_ERROR
