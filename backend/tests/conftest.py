import os
import tempfile

import pytest

os.environ["MEDIA_ROOT"] = tempfile.mkdtemp(prefix="personal-lab-test-media-")

@pytest.fixture(autouse=True)
def reset_rate_limit_state():
    from app import main
    main._rate_window.clear()
    yield
    main._rate_window.clear()
