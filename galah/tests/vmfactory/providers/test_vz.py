# internal
from galah.vmfactory.providers.vz import *

# external
import pytest

@pytest.fixture
def vz(request):
    raw_config = request.config.getoption("--openvz")
    if not raw_config:
        pytest.skip("Configuration with `--openvz` required for this test.")
    config = eval(raw_config)

    provider = OpenVZProvider(**config)
    provider.container_description = "galah-created:test"
    return provider

class TestOpenVZProvider:
    """
    Tests to ensure that the OpenVZProvider class works as expected.

    .. warning::

        It is not a good idea to manipulate/create/destroy containers while
        this test is running as it may get confused (there are certain race
        conditions in the testing code that come into play). At least make sure
        that the range of virtual machines

    """

    def test_run_vzctl_smoke(self, vz):
        """A smoke test to make sure that ``vzctl`` is available."""

        assert vz._run_vzctl(["--version"]) == 0

    def test_get_containers_smoke(self, vz):
        """A smoke test to make sure that ``_get_containers`` doesn't error."""

        vz._get_containers(False)
        vz._get_containers(True)

    def test_create_destroy(self, vz):
        """Tests creating and destroying a virtual machine."""

        containers_before = vz._get_containers(False)
        print "Containers extant before creation: %r" % (containers_before, )

        try:
            created_vm = vz.create_vm()
        finally:
            containers_after = vz._get_containers(False)
            print "Containers extant after creation: %r" % (containers_after, )

            # This will tell you if there was any created containers (though
            # it could get fooled by other VMs getting created at the same
            # time or various other race conditions)
            print "Difference: %r" % (
                set(containers_after) - set(containers_before))

        assert isinstance(created_vm, unicode)
        assert int(created_vm) in vz._get_containers(True)
        assert int(created_vm) in vz._get_containers(False)

        print "Created VM: ", created_vm

        assert vz.destroy_vm(created_vm) is None
        assert int(created_vm) not in vz._get_containers(True)
        assert int(created_vm) not in vz._get_containers(False)

