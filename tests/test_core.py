def test_package_import():
    """Verify the src layout is working and the package is discoverable."""
    import fcm_console_receiver
    assert fcm_console_receiver.__name__ == "fcm_console_receiver"
