from fcm_console_receiver.show_notifications import handle_status


def test_handle_status(captured_print):
    handle_status("CONNECTED", "test_client")
    assert "CONNECTED" in captured_print()
