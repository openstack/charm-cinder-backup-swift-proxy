Cinder Backup to external Swift
-------------------------------

Overview
========

Support for backing up volumes to external swift.
Cinder-backup service configuration is propagated to the cinder charm.

In order to use it external swift URL is needed along with authentication details.


To use:

    juju deploy cinder
    juju deploy cinder-backup-swift-proxy
    juju add-relation cinder-backup-swift-proxy cinder


# Bugs

Please report bugs on [Launchpad](https://bugs.launchpad.net/charm-cinder-backup-swift-proxy/+filebug).
For general questions please refer to the OpenStack [Charm Guide](https://github.com/openstack/charm-guide).