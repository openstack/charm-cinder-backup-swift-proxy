Cinder Backup Service
-------------------------------

Overview
========

This charm provides a Cinder Backup component as part of OpenStack Cinder service.
It is intended to be used alongside the other OpenStack components, even though it must
have relation set up with core Cinder service.


To use:

    juju deploy cinder
    juju deploy -n 3 ceph
    juju deploy cinder-backup
    juju add-relation cinder-backup cinder
    juju add-relation cinder-backup ceph

Configuration
=============
