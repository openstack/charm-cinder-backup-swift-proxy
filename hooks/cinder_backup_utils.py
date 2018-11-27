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

from collections import OrderedDict

from charmhelpers.core.hookenv import (
    config,
)
from charmhelpers.contrib.openstack import (
    templating,
)
from charmhelpers.contrib.openstack.utils import (
    get_os_codename_package,
)
from base64 import b64decode
from charmhelpers.core.host import (
    install_ca_cert,
)


PACKAGES = [
    'cinder-backup',
]
VERSION_PACKAGE = 'cinder-common'
CINDER_CONF = '/etc/cinder/cinder.conf'
TEMPLATES = 'templates/'

# Map config files to hook contexts and services that will be associated
# with file in restart_on_changes()'s service map.
CONFIG_FILES = {}
REQUIRED_INTERFACES = {}


def register_configs():
    """Register config files with their respective contexts.

    Registration of some configs may not be required depending on
    existing of certain relations.
    """
    # if called without anything installed (eg during install hook)
    # just default to earliest supported release. configs dont get touched
    # till post-install, anyway.
    release = get_os_codename_package('cinder-common', fatal=False) or 'folsom'
    configs = templating.OSConfigRenderer(templates_dir=TEMPLATES,
                                          openstack_release=release)
    return configs


def restart_map():
    """Determine the correct resource map to be passed to
    charmhelpers.core.restart_on_change() based on the services configured.

    :returns: dict: A dictionary mapping config file to lists of services
                    that should be restarted when file changes.
    """
    _map = []
    for f, ctxt in CONFIG_FILES.iteritems():
        svcs = []
        for svc in ctxt['services']:
            svcs.append(svc)
        if svcs:
            _map.append((f, svcs))
    return OrderedDict(_map)


def configure_ca():
    ca_cert = config('ssl-ca')
    if ca_cert:
        install_ca_cert(b64decode(ca_cert))
