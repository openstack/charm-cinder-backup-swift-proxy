import cinder_backup_contexts as contexts

from test_utils import (
    CharmTestCase
)

TO_PATCH = [
    'is_relation_made',
    'service_name',
    'get_os_codename_package'
]


class TestCinderBackupContext(CharmTestCase):

    def setUp(self):
        super(TestCinderBackupContext, self).setUp(contexts, TO_PATCH)

    def test_backup_context(self):
        self.get_os_codename_package.return_value = 'icehouse'
        self.service_name.return_value = 'cinder-backup-ut'
        ctxt = contexts.CephBackupSubordinateContext()()
        exp = {'cinder': {'/etc/cinder/cinder.conf':
                          {'sections': {'DEFAULT':
                                        [('backup_driver',
                                          'cinder.backup.drivers.ceph'),
                                         ('backup_ceph_pool',
                                          'cinder-backup-ut'),
                                         ('backup_ceph_user',
                                          'cinder-backup-ut')]}}}}
        self.assertEqual(ctxt, exp)

    def test_backup_context_unsupported(self):
        self.get_os_codename_package.return_value = 'havana'
        self.assertRaises(Exception, contexts.CephBackupSubordinateContext())
