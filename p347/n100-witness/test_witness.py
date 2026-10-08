import hashlib,importlib.util,pathlib,tempfile
spec=importlib.util.spec_from_file_location("capture",pathlib.Path(__file__).with_name("capture.py"))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
def test_sha256_stable():
    with tempfile.TemporaryDirectory() as d:
        p=pathlib.Path(d)/"x"; p.write_bytes(b"abc")
        assert m.sha256(p)==hashlib.sha256(b"abc").hexdigest()
