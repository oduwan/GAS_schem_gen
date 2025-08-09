import shutil
import tempfile

import pytest


@pytest.fixture()
def tempdir():
    d = tempfile.mkdtemp()
    try:
        yield d
    finally:
        shutil.rmtree(d, ignore_errors=True)
