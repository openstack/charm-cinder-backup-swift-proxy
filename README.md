Cinder Backup Service
-------------------------------

Overview
========

This charm provides a 

To use:

    juju deploy cinder
    juju deploy -n 3 ceph
    juju deploy cinder-backup
    juju add-relation cinder-backup cinder
    juju add-relation cinder-backup ceph

Configuration
=============
