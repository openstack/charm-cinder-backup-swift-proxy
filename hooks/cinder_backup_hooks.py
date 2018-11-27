#!/usr/bin/python
#
# Copyright 2016 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import json

from cinder_backup_utils import (
    register_configs,
    restart_map,
    PACKAGES,
    configure_ca,
    REQUIRED_INTERFACES,
)
from cinder_backup_contexts import (
    SwiftBackupSubordinateContext
)
from charmhelpers.core.hookenv import (
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
from charmhelpers.contrib.openstack.utils import (
    set_unit_paused,
    set_unit_upgrading,
    clear_unit_paused,
    clear_unit_upgrading,
    set_os_workload_status,
)
from charmhelpers.payload.execd import execd_preinstall

hooks = Hooks()
CONFIGS = register_configs()


@hooks.hook('install')
def install():
    execd_preinstall()
    apt_update(fatal=True)
    apt_install(PACKAGES, fatal=True)


@hooks.hook('config-changed')
@restart_on_change(restart_map())
def write_and_restart():
    CONFIGS.write_all()
    for rid in relation_ids('backup-backend'):
        backup_backend_joined(rid)

    for svc in ['cinder-backup']:
        service_restart(svc)


@hooks.hook('backup-backend-relation-joined')
def backup_backend_joined(rel_id=None):
    ctxt = SwiftBackupSubordinateContext()()
    relation_set(
        relation_id=rel_id,
        backend_name=service_name(),
        subordinate_configuration=json.dumps(ctxt)
    )
    relation_set(relation_id=rel_id, stateless=True)
    configure_ca()


@hooks.hook('backup-backend-relation-changed')
def backup_backend_changed():
    # NOTE(jamespage) recall backup_backend as this only ever
    # changes post initial creation if the cinder charm is upgraded to a new
    # version of openstack.
    backup_backend_joined()


@hooks.hook('upgrade-charm')
@restart_on_change(restart_map())
def upgrade_charm():
    CONFIGS.write_all()
    for rid in relation_ids('backup-backend'):
        backup_backend_joined(rid)


@hooks.hook('pre-series-upgrade')
def pre_series_upgrade():
    log("Running prepare series upgrade hook", "INFO")
    # In order to indicate the step of the series upgrade process for
    # administrators and automated scripts, the charm sets the paused and
    # upgrading states.
    set_unit_paused()
    set_unit_upgrading()


@hooks.hook('post-series-upgrade')
def post_series_upgrade():
    log("Running complete series upgrade hook", "INFO")
    # In order to indicate the step of the series upgrade process for
    # administrators and automated scripts, the charm clears the paused and
    # upgrading states.
    clear_unit_paused()
    clear_unit_upgrading()


if __name__ == '__main__':
    try:
        hooks.execute(sys.argv)
    except UnregisteredHookError as e:
        log('Unknown hook {} - skipping.'.format(e))
    set_os_workload_status(CONFIGS, REQUIRED_INTERFACES)
