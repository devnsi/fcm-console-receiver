import json

from fcm_console_receiver.show_notifications import handle_data


def test_handle_payload_full(captured_print):
    # given
    payload = json.dumps({
        "notification": {
            "title": "System Alert",
            "body": "Database backup completed successfully."
        },
        "data": {
            "google.c.a.ts": "1775932262",  # Should be filtered out
            "custom_id": "998877",  # Should be kept
            "priority_level": "high"  # Should be kept
        },
        "from": "/topics/alerts"
    }).encode('utf-8')
    # when
    handle_data(payload, "test_client")
    # then
    assert "System Alert" in captured_print()
    assert "Database backup completed successfully" in captured_print()
    assert "@alerts" in captured_print()
    assert "priority_level" in captured_print()


def test_handle_payload_sparse(captured_print):
    # given
    payload = json.dumps({
        "notification": {
            "body": "Database backup completed successfully."
        }
    }).encode('utf-8')
    # when
    handle_data(payload, "test_client")
    # then
    assert "Notification" in captured_print()
    assert "Database backup completed successfully" in captured_print()


def test_handle_payload_custom(captured_print):
    # given
    payload = json.dumps({
        "data": {
            "google.c.a.ts": "1775932262",  # Should be filtered out
            "custom_id": "998877",  # Should be kept
            "priority_level": "high"  # Should be kept
        }
    }).encode('utf-8')
    # when
    handle_data(payload, "test_client")
    # then
    assert "custom_id" in captured_print()
    assert "google.c.a.ts" not in captured_print()


def test_handle_payload_repeated(captured_print):
    # given
    def payload(n: int):
        return json.dumps({
            "notification": {
                "body": f"Database increment {n} backup completed successfully."
            }
        }).encode('utf-8')

    # when
    for i in range(3):
        handle_data(payload(i), "test_client")
        # then
        assert f"Database increment {i}" in captured_print()
