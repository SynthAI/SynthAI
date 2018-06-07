from .. import tutils, mastertest
from mitmproxy.addons import stickyauth
from mitmproxy import master
from mitmproxy import options
from mitmproxy import proxy


class TestStickyAuth(mastertest.MasterTest):
    def test_simple(self):
        o = options.Options(stickyauth = ".*")
        m = master.Master(o, proxy.DummyServer())
        sa = stickyauth.StickyAuth()
        m.addons.add(sa)

        f = tutils.tflow(resp=True)
        f.request.headers["authorization"] = "foo"
        m.request(f)

        assert "address" in sa.hosts

        f = tutils.tflow(resp=True)
        m.request(f)
        assert f.request.headers["authorization"] == "foo"
