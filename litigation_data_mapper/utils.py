import inspect
import os

import boto3
from prefect.settings import PREFECT_UI_URL
from prefect_slack.credentials import SlackWebhook


def get_ssm_parameter(param_name: str) -> str:
    """
    Get a parameter value from AWS SSM Parameter Store

    :param str param_name: Name of the parameter to be fetched.
    :return str: The value of the parameter as set in AWS.
    """
    ssm = boto3.client("ssm", region_name="eu-west-1")
    response = ssm.get_parameter(Name=param_name, WithDecryption=True)
    return response["Parameter"]["Value"]


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
    slack_channel_name = "alerts-platform"

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
