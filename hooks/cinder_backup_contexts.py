from charmhelpers.core.hookenv import (
    service_name,
    is_relation_made,
)
from charmhelpers.contrib.openstack.context import (
    OSContextGenerator,
)
from charmhelpers.contrib.openstack.utils import get_os_codename_package


class CephBackupSubordinateContext(OSContextGenerator):
    interfaces = ['ceph-cinder']

    def __call__(self):
        """Used to generate template context to be added to cinder.conf in the
        presence of a ceph relation.
        """
        if not is_relation_made('ceph', 'key'):
            return {}

        if get_os_codename_package('cinder-common') < "icehouse":
            raise Exception("Unsupported version of Openstack")

        service = service_name()
        backup_driver = 'cinder.backup.drivers.ceph'
        return {
            "cinder": {
                "/etc/cinder/cinder.conf": {
                    "sections": {
                        'DEFAULT': [
                            ('backup_driver', backup_driver),
                            ('backup_ceph_pool', service),
                            ('backup_ceph_user', service),
                        ]
                    }
                }
            }
        }
