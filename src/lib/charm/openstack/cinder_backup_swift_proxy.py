
from charmhelpers.core.hookenv import (
    config,
    status_set
)
from charmhelpers.core.host import install_ca_cert
from base64 import b64decode

from charmhelpers.contrib.openstack.context import OSContextGenerator
from charmhelpers.contrib.openstack.utils import get_os_codename_package, \
    CompareOpenStackReleases
from charms_openstack.charm import OpenStackCharm


class CinderBackupSwiftCharm(OpenStackCharm):
    name = 'cinder-backup-swift-proxy'
    packages = ['cinder-backup']
    release = 'queens'

    def get_swift_backup_config(self):
        status_set('active', 'Unit is ready')
        name = "cinder-backup"
        return name, SwiftBackupSubordinateContext()()

    def configure_ca(self):
        ca_cert = config('ssl-ca')
        if ca_cert:
            install_ca_cert(b64decode(ca_cert))


class SwiftBackupSubordinateContext(OSContextGenerator):
    interfaces = ['backup-backend']

    def __call__(self):
        """Used to generate template context to be added to cinder.conf.
        """

        release = get_os_codename_package('cinder-common')
        if CompareOpenStackReleases(release) < "queens":
            raise Exception("Unsupported version of Openstack")

        backup_driver = 'cinder.backup.drivers.swift.SwiftBackupDriver'
        backup_auth_method = 'single_user'
        if config('auth-version') == 2:
            ctxt = [
                ('backup_driver', backup_driver),
                ('backup_swift_auth', backup_auth_method),
                ('backup_swift_auth_version', config('auth-version')),
                ('backup_swift_url', config('endpoint-url')),
                ('backup_swift_auth_url', config('auth-url')),
                ('backup_swift_user', config('swift-user')),
                ('backup_swift_key', config('swift-key')),
                ('backup_swift_container', config('container-name')),
                ('backup_swift_object_size', config('object-size')),
                ('backup_swift_block_size', config('block-size')),
                ('backup_swift_tenant', config('tenant-name'))
            ]
        elif config('auth-version') == 3:
            ctxt = [
                ('backup_driver', backup_driver),
                ('backup_swift_auth', backup_auth_method),
                ('backup_swift_auth_version', config('auth-version')),
                ('backup_swift_url', config('endpoint-url')),
                ('backup_swift_auth_url', config('auth-url')),
                ('backup_swift_user', config('swift-user')),
                ('backup_swift_key', config('swift-key')),
                ('backup_swift_container', config('container-name')),
                ('backup_swift_object_size', config('object-size')),
                ('backup_swift_block_size', config('block-size')),
                ('backup_swift_user_domain', config('user-domain')),
                ('backup_swift_project_domain', config('project-domain')),
                ('backup_swift_project', config('project-name'))
            ]
        else:
            raise Exception("Unsupported swift auth version")
        return {
            "cinder": {
                "/etc/cinder/cinder.conf": {
                    "sections": {
                        'DEFAULT': ctxt
                    }
                }
            }
        }
