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

from charmhelpers.core.hookenv import (
    config,
)
from charmhelpers.contrib.openstack.context import (
    OSContextGenerator,
)
from charmhelpers.contrib.openstack.utils import (
    get_os_codename_package,
    CompareOpenStackReleases,
)


class SwiftBackupSubordinateContext(OSContextGenerator):
    def __call__(self):
        """Used to generate template context to be added to cinder.conf.
        """

        release = get_os_codename_package('cinder-common')
        if CompareOpenStackReleases(release) < "queens":
            raise Exception("Unsupported version of Openstack")

        backup_driver = 'cinder.backup.drivers.swift.SwiftBackupDriver'
        backup_auth_method = 'single_user'
        if config('auth-version') == 2:
            ctxt = {
                "cinder": {
                    "/etc/cinder/cinder.conf": {
                        "sections": {
                            'DEFAULT': [
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
                                ('backup_swift_tenant', config('tenant-name')),
                            ]
                        }
                    }
                }
            }
        elif config('auth-version') == 3:
            ctxt = {
                "cinder": {
                    "/etc/cinder/cinder.conf": {
                        "sections": {
                            'DEFAULT': [
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
                                ('backup_swift_project', config('project-name')),
                            ]
                        }
                    }
                }
            }
        else:
            raise Exception("Unsupported swift auth version")
        return ctxt
