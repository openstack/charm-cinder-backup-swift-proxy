import charms.reactive as reactive
import charms_openstack.charm as charmclass
import charms_openstack.charm
import charm.openstack.cinder_backup_swift as cinder_backup_swift
assert cinder_backup_swift
import charms.reactive.flags as flags

charms_openstack.charm.defaults.use_defaults(
    'charm.installed',
    'update-status')

flags.register_trigger(when='config.changed',
                       clear_flag='cinder.configured')
flags.register_trigger(when='config.changed',
                       clear_flag='cinder-backup.started')
flags.register_trigger(when='upgraded', clear_flag='config.rendered')


@reactive.when('cinder-backup.available')
@reactive.when_not('cinder.configured')
def render_config(principle):
    with charmclass.provide_charm_instance() as charm_class:
        name, config = charm_class.get_swift_config()
        principle.configure_principal(name, config)
        charm_class.configure_ca()
        reactive.set_state('cinder.configured')
