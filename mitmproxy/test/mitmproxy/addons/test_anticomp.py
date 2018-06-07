from .. import tutils, mastertest
from mitmproxy.addons import anticomp
from mitmproxy import master
from mitmproxy import options
from mitmproxy import proxy


class TestAntiComp(mastertest.MasterTest):
    def test_simple(self):
        o = options.Options(anticomp = True)
        m = master.Master(o, proxy.DummyServer())
        sa = anticomp.AntiComp()
        m.addons.add(sa)

        f = tutils.tflow(resp=True)
        m.request(f)

        f = tutils.tflow(resp=True)

        f.request.headers["Accept-Encoding"] = "foobar"
        m.request(f)
        assert f.request.headers["Accept-Encoding"] == "identity"
