import tempfile
import shutil
import os
import unittest

import log_analyzer


finder_test_params = [
    # testname  |  files in dir  |  found log
    (
        'empty dir', [], None
    ),
    (
        'other files, no logs',
        ['other_file1', 'other_file2'],
        None
    ),
    (
        'several logs, plain and .gz',
        ['nginx-access-ui.log-20170630.gz'],
        'nginx-access-ui.log-20170630.gz'
    )
]


class TestFindLatestLog(unittest.TestCase):
    def setUp(self):
        self.testdirs = []

    def tearDown(self):
        for testdir in self.testdirs:
            shutil.rmtree(testdir)

    def _prepare_testdir(self, filenames):
        testdir = tempfile.mkdtemp()
        print(testdir)
        self.testdirs.append(testdir)
        for filename in filenames:
            filepath = os.path.join(testdir, filename)
            open(filepath, 'w').close()

        return testdir

    def test_finder(self):
        for test_name, files_list, result in finder_test_params:
            with self.subTest(test_name=test_name):
                testdir = self._prepare_testdir(files_list)
                found_logfile = log_analyzer.find_latest_log(testdir)
                self.assertEqual(found_logfile, result)
