from unittest.mock import patch

import pytest


@pytest.fixture
def captured_print():
    """Fixture that captures print calls but still displays them."""
    print_actual = print

    def side_effect(*args, **kwargs):
        print_actual(*args, **kwargs)

    with patch('builtins.print', side_effect=side_effect) as mocked_print:
        yield lambda: mocked_print.call_args[0][0] if mocked_print.called else ""
