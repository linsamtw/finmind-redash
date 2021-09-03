import json
from redash.client import Redash

with open("dashboard/template.json") as json_file:
    dashboard_json = json.load(json_file)

api = Redash()
new_dashboard = api.create_dashboard_by_json(
    dashboard_name="template666", dashboard_json=dashboard_json
)
