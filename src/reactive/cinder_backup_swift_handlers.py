import charms.reactive as reactive
import charms_openstack

# This charm's library contains all of the handler code associated with
# cinder-backup-swift-proxy -- we need to import it to get the definitions
# for the charm.
import charm.openstack.cinder_backup_swift_proxy  # noqa
import charms.reactive.flags as flags
from charms.reactive.relations import (
    endpoint_from_flag,
)

charms_openstack.charm.defaults.use_defaults(
    'charm.installed',
    'upgrade-charm',
)

flags.register_trigger(when='config.changed', clear_flag='config.complete')
flags.register_trigger(when='upgraded', clear_flag='config.complete')
flags.register_trigger(when='endpoint.backup-backend.changed',
                       clear_flag='config.complete')


@reactive.when('backup-backend.available')
@reactive.when_not('config.complete')
def configure_cinder_backup():
    # don't always have a relation context - obtain from the flag
    endp = endpoint_from_flag('endpoint.backup-backend.joined')
    with charms_openstack.charm.provide_charm_instance() as charm_instance:
        # publish config options for all remote units of a given rel
        name, config = charm_instance.get_swift_backup_config()
        endp.publish(name, config)
        charm_instance.configure_ca()
        flags.set_flag('config.complete')


@reactive.hook('config-changed')
def update_config():
    reactive.remove_state('config.complete')
