import io
import os
import uuid
from typing import Union

import swiftclient
from _pytest.config import Config, ExitCode
from _pytest.main import Session
from _pytest.terminal import TerminalReporter
from swiftclient import ClientException


class HTMLSwift:
    def __init__(self, config: Config):
        self.config = config
        self.os_endpoint = os.environ.get("OBJECT_STORAGE_ENDPOINT")
        self.os_bucket = os.environ.get("OBJECT_STORAGE_BUCKET")
        self.os_username = os.environ.get("OBJECT_STORAGE_USERNAME")
        self.os_password = os.environ.get("OBJECT_STORAGE_PASSWORD")
        self.os_tenant_id = os.environ.get("OBJECT_STORAGE_TENANT_ID")
        self.os_tenant_name = os.environ.get("OBJECT_STORAGE_TENANT_NAME")
        self.os_region_name = os.environ.get("OBJECT_STORAGE_REGION_NAME")
        self.os_retention = self._get_retention()
        self.os_policy = self._get_policy()
        self.access_url = None

    @staticmethod
    def _get_policy() -> str:
        policy = os.environ.get("OBJECT_STORAGE_POLICY")
        if not policy or policy == "download":
            return "download"
        else:
            return ""

    @staticmethod
    def _get_retention() -> int:
        retention = os.environ.get("OBJECT_STORAGE_RETENTION")
        if retention and int(retention) > 0:
            return int(retention) * 24 * 60 * 60
        else:
            return 0

    def get_access_url(self, name: str) -> str:
        self.access_url = (
            f"https://{self.os_bucket}.auth-{self.os_tenant_id}.storage."
            f"{self.os_region_name.lower()}.cloud.ovh.net/{name}"
        )
        return self.access_url

    def send_html(self, name, content: str):
        conn = swiftclient.Connection(
            user=self.os_username,
            key=self.os_password,
            authurl=self.os_endpoint,
            auth_version="3",
            os_options={
                "tenant_id": self.os_tenant_id,
                "tenant_name": self.os_tenant_name,
                "region_name": self.os_region_name,
            },
        )
        try:
            result = conn.get_container(self.os_bucket)
            print(result)
        except ClientException as e:
            if e.http_status == 404:
                print("Bucket does not exist")
                if self.os_policy == "download":
                    try:
                        result = conn.put_container(
                            self.os_bucket,
                            headers={"X-Container-Read": ".r:*,.rlistings"},
                        )
                        print(result)
                        print(
                            "Create bucket "
                            + self.os_bucket
                            + " with policy public successfully!"
                        )
                    except ClientException as e:
                        print(e.http_status, e.msg)
                        exit(1)
                else:
                    result = conn.put_container(self.os_bucket)
                    print(result)
                    print("Create bucket " + self.os_bucket + " successfully!")

        # upload file to Swift storage
        with io.StringIO(content) as f:
            if self.os_retention:
                try:
                    result = conn.put_object(
                        self.os_bucket,
                        name,
                        contents=f.read(),
                        content_type="text/html",
                        headers={"X-Delete-After": self.os_retention},
                    )
                    print(result)
                    print(
                        f"Create object successfully with retention ! objectUrl: {self.get_access_url(name)}"
                    )
                except ClientException as e:
                    print(e.http_status, e.msg)
                    exit(1)
            else:
                result = conn.put_object(
                    self.os_bucket,
                    name,
                    contents=f.read(),
                    content_type="text/html",
                )
                print(result)
                print(
                    f"Create object successfully! objectUrl: {self.get_access_url(name)}"
                )

    def pytest_sessionfinish(self, session: Session, exitstatus: Union[int, ExitCode]):
        html = getattr(session.config, "_html", None)
        if html:
            html._post_process_reports()
            name = f"{str(uuid.uuid4())}/report.html"
            self.send_html(name, html._generate_report(session))
            session.config._report_url = self.get_access_url(name)

    def pytest_terminal_summary(
        self,
        terminalreporter: TerminalReporter,
        exitstatus: Union[int, ExitCode],
        config: Config,
    ):
        terminalreporter.write_sep(
            "-", f"HTML report sent on Swift object storage at {self.access_url}"
        )