import inspect
import os

from prefect.settings import PREFECT_UI_URL
from prefect_slack.credentials import SlackWebhook


class SlackNotify:
    """Notify a Slack channel through a Prefect Slack webhook."""

    # Message templates
    FLOW_RUN_URL = "{prefect_base_url}/flow-runs/flow-run/{flow_run.id}"
    BASE_MESSAGE = (
        "💥 Flow run <{ui_url}|{flow.name}/{flow_run.name}> "
        "state `{flow_run.state.name}` at {flow_run.state.timestamp}.\n"
        "Error message: {state.message}"
    )

    # Block name
    slack_channel_name = "prod_updates"

    @classmethod
    def get_environment(cls) -> str:
        """Get the current environment."""
        return os.getenv("AWS_ENV", "sandbox")

    @classmethod
    def get_slack_block_name(cls) -> str:
        """Get the slack block name for the current environment."""
        return f"slack-webhook-{cls.slack_channel_name}-prefect-mvp-{cls.get_environment()}"

    @classmethod
    async def message(cls, flow, flow_run, state):
        """
        Send a notification to a Slack channel about the state of a Prefect flow run.

        Intended to be called from prefect flow hooks:

        ```python
        @flow(on_failure=[SlackNotify.message])
        def my_flow():
            pass
        ```
        """
        if cls.get_environment() != "prod":
            return None

        ui_url = cls.FLOW_RUN_URL.format(
            prefect_base_url=PREFECT_UI_URL.value(), flow_run=flow_run
        )
        msg = cls.BASE_MESSAGE.format(
            flow=flow,
            flow_run=flow_run,
            state=state,
            ui_url=ui_url,
            environment=cls.get_environment(),
        )

        slack = SlackWebhook.load(cls.get_slack_block_name())
        if inspect.isawaitable(slack):
            slack = await slack

        result = slack.notify(body=msg)
        if inspect.isawaitable(result):
            _ = await result

        return None
