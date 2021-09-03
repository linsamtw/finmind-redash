from redash.client import Redash


# test
for fork_name in ["Japan", "Taiwan", "Hong Kong", "United States"]:
    dashboard_params = fork_name
    current_name = "template"
    self = Redash()
    new_dashboard = self.fork_dashboard(
        current_name=current_name, fork_name=fork_name
    )
    slug = new_dashboard["slug"]
    self.set_dashboard_text(slug=slug, text=fork_name)
    self.set_dashboard_params(slug=slug, params=dashboard_params)
