from unittest.mock import patch
import pytest
from django_rq import get_queue
from orders.services.notifications import notify_order_status, publish_new_order

@pytest.mark.django_db
class TestOrderTasks:
    def test_notify_order_status_queuing(self):
        """Verify that .delay() queues the task in Redis."""
        queue = get_queue("default")
        queue.empty()  # start clean
        
        notify_order_status.delay(telegram_id=123, order_id=456, status="paid")
        
        assert queue.count == 1
        job = queue.jobs[0]
        assert job.func_name == "orders.services.notifications.notify_order_status"
        assert job.args == (123, 456, "paid")

    def test_publish_new_order_queuing(self):
        """Verify that .delay() queues the task in Redis."""
        queue = get_queue("default")
        queue.empty()
        
        publish_new_order.delay(order_id=789)
        
        assert queue.count == 1
        job = queue.jobs[0]
        assert job.func_name == "orders.services.notifications.publish_new_order"
        assert job.args == (789,)

    @patch("httpx.post")
    @patch("os.environ.get")
    def test_notify_order_status_execution(self, mock_env, mock_post):
        """Verify the task logic itself (mocking external calls)."""
        mock_env.return_value = "fake-token"
        mock_post.return_value.status_code = 200
        
        # Test synchronous execution of the job function
        notify_order_status(telegram_id=123, order_id=456, status="paid")
        
        assert mock_post.called
        args, kwargs = mock_post.call_args
        assert "botfake-token/sendMessage" in args[0]
        assert kwargs["json"]["chat_id"] == 123
        assert "Оплачен" in kwargs["json"]["text"]

    @patch("orders.services.notifications._get_redis_client")
    def test_publish_new_order_execution(self, mock_redis_client):
        """Verify the publishing logic itself."""
        publish_new_order(order_id=789)
        
        assert mock_redis_client.return_value.publish.called
        mock_redis_client.return_value.publish.assert_called_with("new_order", 789)
