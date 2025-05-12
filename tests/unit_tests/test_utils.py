from unittest.mock import AsyncMock, patch

import pytest

from litigation_data_mapper.utils import SlackNotify


@pytest.mark.asyncio
async def test_message_sends_notification_in_prod(
    mock_prefect_slack_webhook, mock_flow, mock_flow_run
):
    with patch.dict("os.environ", {"AWS_ENV": "prod"}), patch(
        "litigation_data_mapper.utils.PREFECT_UI_URL"
    ) as mock_ui_url:
        mock_ui_url.value.return_value = "http://127.0.0.1:1234"

        await SlackNotify.message(mock_flow, mock_flow_run, mock_flow_run.state)
        mock_SlackWebhook, mock_prefect_slack_block = mock_prefect_slack_webhook

        # Verify webhook was loaded
        mock_SlackWebhook.load.assert_called_once_with(
            "slack-webhook-platform-prefect-mvp-prod"
        )

        # Verify notification was sent
        mock_prefect_slack_block.notify.assert_called_once()
        message = mock_prefect_slack_block.notify.call_args.kwargs.get("body", "")

        # Check message contains key information without being too strict about format
        assert "TestFlow/TestFlowRun" in message
        assert "Completed" in message
        assert "prod" in message
        assert "test-flow-run-id" in message
        assert "message" in message
        assert "http://127.0.0.1:1234" in message


@pytest.mark.asyncio
async def test_message_skips_notification_in_non_prod(
    mock_prefect_slack_webhook, mock_flow, mock_flow_run
):
    await SlackNotify.message(mock_flow, mock_flow_run, mock_flow_run.state)
    mock_SlackWebhook, mock_prefect_slack_block = mock_prefect_slack_webhook

    # Verify no webhook was loaded
    mock_SlackWebhook.load.assert_not_called()
    # Verify no notification was sent
    mock_prefect_slack_block.notify.assert_not_called()


@pytest.mark.asyncio
async def test_message_handles_async_webhook(
    mock_prefect_slack_webhook, mock_flow, mock_flow_run
):
    with patch.dict("os.environ", {"AWS_ENV": "prod"}), patch(
        "litigation_data_mapper.utils.PREFECT_UI_URL"
    ) as mock_ui_url:
        mock_ui_url.value.return_value = "http://127.0.0.1:1234"

        mock_SlackWebhook, mock_prefect_slack_block = mock_prefect_slack_webhook
        # Make the webhook load return an awaitable
        mock_webhook = AsyncMock()
        mock_webhook.notify = AsyncMock()
        mock_SlackWebhook.load.return_value = mock_webhook

        await SlackNotify.message(mock_flow, mock_flow_run, mock_flow_run.state)

        # Verify webhook was loaded and notification was sent
        mock_SlackWebhook.load.assert_called_once()
        mock_webhook.notify.assert_called_once()


@pytest.mark.asyncio
async def test_message_handles_webhook_load_failure(
    mock_prefect_slack_webhook, mock_flow, mock_flow_run
):
    with patch.dict("os.environ", {"AWS_ENV": "prod"}), patch(
        "litigation_data_mapper.utils.PREFECT_UI_URL"
    ) as mock_ui_url:
        mock_ui_url.value.return_value = "http://127.0.0.1:1234"
        mock_SlackWebhook, _ = mock_prefect_slack_webhook
        mock_SlackWebhook.load.side_effect = Exception("Failed to load webhook")

        with pytest.raises(Exception, match="Failed to load webhook"):
            await SlackNotify.message(mock_flow, mock_flow_run, mock_flow_run.state)


@pytest.mark.asyncio
async def test_message_handles_notify_failure(
    mock_prefect_slack_webhook, mock_flow, mock_flow_run
):
    with patch.dict("os.environ", {"AWS_ENV": "prod"}), patch(
        "litigation_data_mapper.utils.PREFECT_UI_URL"
    ) as mock_ui_url:
        mock_ui_url.value.return_value = "http://127.0.0.1:1234"
        mock_SlackWebhook, _ = mock_prefect_slack_webhook
        mock_webhook = AsyncMock()
        mock_webhook.notify.side_effect = Exception("Failed to send notification")
        mock_SlackWebhook.load.return_value = mock_webhook

        with pytest.raises(Exception, match="Failed to send notification"):
            await SlackNotify.message(mock_flow, mock_flow_run, mock_flow_run.state)


@pytest.mark.asyncio
async def test_message_handles_missing_attributes(
    mock_prefect_slack_webhook, mock_flow, mock_flow_run
):
    with patch.dict("os.environ", {"AWS_ENV": "prod"}), patch(
        "litigation_data_mapper.utils.PREFECT_UI_URL"
    ) as mock_ui_url:
        mock_ui_url.value.return_value = "http://127.0.0.1:1234"
        # Remove required attributes
        delattr(mock_flow_run, "name")
        delattr(mock_flow_run.state, "message")

        with pytest.raises(AttributeError):
            await SlackNotify.message(mock_flow, mock_flow_run, mock_flow_run.state)


@pytest.mark.asyncio
async def test_message_handles_missing_environment(
    mock_prefect_slack_webhook, mock_flow, mock_flow_run
):
    with patch.dict("os.environ", {}, clear=True), patch(
        "litigation_data_mapper.utils.PREFECT_UI_URL"
    ) as mock_ui_url:
        mock_ui_url.value.return_value = "http://127.0.0.1:1234"

        await SlackNotify.message(mock_flow, mock_flow_run, mock_flow_run.state)
        mock_SlackWebhook, _ = mock_prefect_slack_webhook

        # Should not attempt to send notification in non-prod environment
        mock_SlackWebhook.load.assert_not_called()


@pytest.mark.asyncio
async def test_message_formatting(mock_prefect_slack_webhook, mock_flow, mock_flow_run):
    with patch.dict("os.environ", {"AWS_ENV": "prod"}), patch(
        "litigation_data_mapper.utils.PREFECT_UI_URL"
    ) as mock_ui_url:
        mock_ui_url.value.return_value = "http://127.0.0.1:1234"
        _, mock_prefect_slack_block = mock_prefect_slack_webhook

        await SlackNotify.message(mock_flow, mock_flow_run, mock_flow_run.state)

        # Verify notification was sent
        mock_prefect_slack_block.notify.assert_called_once()
        message = mock_prefect_slack_block.notify.call_args.kwargs.get("body", "")

        # Verify exact message format
        expected_url = "http://127.0.0.1:1234/flow-runs/flow-run/test-flow-run-id"
        expected_message = (
            f"Flow run TestFlow/TestFlowRun observed in state `Completed` "
            f"at 2025-01-28T12:00:00+00:00. For environment: prod. "
            f"Flow run URL: {expected_url}. State message: message"
        )
        assert message == expected_message
