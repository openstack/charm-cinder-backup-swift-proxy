#!/usr/bin/python
import os
import sys
import json

from cinder_backup_utils import (
    register_configs,
    restart_map,
    set_ceph_env_variables,
    PACKAGES
)
from cinder_backup_contexts import (
    CephBackupSubordinateContext
)
from charmhelpers.core.hookenv import (
    config,
    Hooks,
    UnregisteredHookError,
    service_name,
    relation_set,
    relation_ids,
    log,
)
from charmhelpers.fetch import apt_install, apt_update
from charmhelpers.core.host import (
    restart_on_change,
    service_restart,
)
from charmhelpers.contrib.storage.linux.ceph import (
    delete_keyring,
    ensure_ceph_keyring,
    is_request_complete,
    CephBrokerRq,
    send_request_if_needed,
)
from charmhelpers.payload.execd import execd_preinstall

hooks = Hooks()
CONFIGS = register_configs()


@hooks.hook('install')
def install():
    execd_preinstall()
    apt_update(fatal=True)
    apt_install(PACKAGES, fatal=True)


@hooks.hook('ceph-relation-joined')
def ceph_joined():
    if not os.path.isdir('/etc/ceph'):
        os.mkdir('/etc/ceph')


def get_ceph_request():
    service = service_name()
    rq = CephBrokerRq()
    replicas = config('ceph-osd-replication-count')
    rq.add_op_create_pool(name=service, replica_count=replicas)
    return rq


@hooks.hook('ceph-relation-changed')
@restart_on_change(restart_map())
def ceph_changed():
    if 'ceph' not in CONFIGS.complete_contexts():
        log('ceph relation incomplete. Peer not ready?')
        return

    service = service_name()
    if not ensure_ceph_keyring(service=service,
                               user='cinder', group='cinder'):
        log('Could not create ceph keyring: peer not ready?')
        return

    if is_request_complete(get_ceph_request()):
        log('Request complete')
        CONFIGS.write_all()
        set_ceph_env_variables(service=service)
        for rid in relation_ids('backup-backend'):
            backup_backend(rid)

        # Ensure that cinder services are restarted since only now can we
        # guarantee that ceph resources are ready. Note that the order of
        # restart is important here.
        for svc in ['cinder-volume', 'cinder-backup']:
            service_restart(svc)

    else:
        send_request_if_needed(get_ceph_request())


@hooks.hook('ceph-relation-broken')
def ceph_broken():
    service = service_name()
    delete_keyring(service=service)
    CONFIGS.write_all()


@hooks.hook('config-changed')
@restart_on_change(restart_map())
def write_and_restart():
    CONFIGS.write_all()


@hooks.hook('backup-backend-relation-joined')
def backup_backend(rel_id=None):
    if 'ceph' not in CONFIGS.complete_contexts():
        log('ceph relation incomplete. Peer not ready?')
    else:
        ctxt = CephBackupSubordinateContext()()
        relation_set(
            relation_id=rel_id,
            backend_name=service_name(),
            subordinate_configuration=json.dumps(ctxt)
        )


@hooks.hook('backup-backend-relation-changed')
def backup_backend_changed():
    # NOTE(jamespage) recall backup_backend as this only ever
    # changes post initial creation if the cinder charm is upgraded to a new
    # version of openstack.
    backup_backend()


@hooks.hook('upgrade-charm')
@restart_on_change(restart_map())
def upgrade_charm():
    if 'ceph' in CONFIGS.complete_contexts():
        CONFIGS.write_all()
        set_ceph_env_variables(service=service_name())
        for rid in relation_ids('backup-backend'):
            backup_backend(rid)


if __name__ == '__main__':
    try:
        hooks.execute(sys.argv)
    except UnregisteredHookError as e:
        log('Unknown hook {} - skipping.'.format(e))
