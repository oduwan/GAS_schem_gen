import shutil, tempfile, pytest

@pytest.fixture()
def tempdir():
    d = tempfile.mkdtemp()
    try:
        yield d
    finally:
        shutil.rmtree(d, ignore_errors=True)