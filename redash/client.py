import requests
from loguru import logger
import typing

REDASH_API_KEY = "NT1Ir006zFO98XCKccNipRdW6PogVdbuDMPZBxPQ"
REDASH_URL = "http://localhost:5000"


class Redash(object):
    def __init__(self):
        self.redash_url = REDASH_URL
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Key {REDASH_API_KEY}"})

    def get_dashboard_list(self):
        resp = requests.get(
            f"{self.redash_url}/api/dashboards",
            params=dict(api_key=REDASH_API_KEY),
        )
        dashboard_list = resp.json()["results"]
        return [dashboard_json["name"] for dashboard_json in dashboard_list]

    def get_dashboard_json(self, name: str):
        resp = requests.get(
            f"{self.redash_url}/api/dashboards/{name}",
            params=dict(api_key=REDASH_API_KEY),
        )
        dashboard = resp.json()
        return dashboard

    def create_dashboard(self, dashboard_name: str):
        # dashboard_json["name"] = "api test 1"
        resp = self.session.post(
            f"{self.redash_url}/api/dashboards",
            json=dict(name=dashboard_name),
        )
        return resp.json()

    def update_dashboard(self, dashboard_id: str, dashboard_json: dict):
        dashboard_id = dashboard_json["id"]
        resp = self.session.post(
            f"{self.redash_url}/api/dashboards/{dashboard_id}",
            json=dashboard_json,
        )
        resp.json()

    def create_widget(
        self, dashboard_id: str, visualization_id: str, text: str, options: str
    ):
        data = {
            "dashboard_id": dashboard_id,
            "visualization_id": visualization_id,
            "text": text,
            "options": options,
            "width": 1,
        }
        resp = self.session.post(
            f"{self.redash_url}/api/widgets",
            json=data,
        )
        if resp.status_code != 200:
            logger.info(resp)
        return resp

    def set_dashboard_text(self, slug: str, text: str):
        resp = self.get_dashboard_json(name=slug)
        # get dashboard text
        widget = [widget for widget in resp["widgets"] if widget["text"]][0]
        widget["text"] = text
        _id = widget["id"]
        resp = self.session.post(
            f"{self.redash_url}/api/widgets/{_id}",
            json=widget,
        )
        if resp.status_code != 200:
            logger.info(resp)

    def set_dashboard_params(self, slug: str, params: str):
        resp = self.get_dashboard_json(slug)
        for widget in resp["widgets"]:
            if widget["text"] == "":
                _id = widget["id"]
                logger.info(f"set_dashboard_params {_id}")
                widget["options"]["parameterMappings"]["country"][
                    "value"
                ] = params
                resp = self.session.post(
                    f"{self.redash_url}/api/widgets/{_id}",
                    json=widget,
                )
                if resp.status_code != 200:
                    logger.info(resp)

    def create_dashboard_by_json(
        self, dashboard_name: str, dashboard_json: str
    ) -> typing.Dict[str, str]:
        new_dashboard = self.create_dashboard(dashboard_name=dashboard_name)
        for widget in dashboard_json["widgets"]:
            visualization_id = None
            if "visualization" in widget:
                visualization_id = widget["visualization"]["id"]
            resp = self.create_widget(
                dashboard_id=new_dashboard["id"],
                visualization_id=visualization_id,
                text=widget["text"],
                options=widget["options"],
            )

    def fork_dashboard(self, current_name: str, fork_name: str = None):
        logger.info(f"fork_dashboard from {current_name} to {fork_name}")
        current_dashboard = self.get_dashboard_json(current_name)
        fork_name = (
            fork_name if fork_name else f"Copy of: {current_dashboard['name']}"
        )
        if fork_name in self.get_dashboard_list():
            raise Exception(f"Duplicate name: {fork_name}")
        new_dashboard = self.create_dashboard(dashboard_name=fork_name)
        if current_dashboard["tags"]:
            self.update_dashboard(
                new_dashboard["id"], {"tags": current_dashboard["tags"]}
            )

        for widget in current_dashboard["widgets"]:
            visualization_id = None
            if "visualization" in widget:
                visualization_id = widget["visualization"]["id"]
            resp = self.create_widget(
                dashboard_id=new_dashboard["id"],
                visualization_id=visualization_id,
                text=widget["text"],
                options=widget["options"],
            )
        return new_dashboard

    def get_publish_url(self, slug: str) -> str:
        # dashboard_json = self.get_dashboard_json(name="template")
        dashboard_json = self.get_dashboard_json(name=slug)
        return dashboard_json.get("public_url", "")
