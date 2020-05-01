import tempfile
import shutil
import os
import unittest
import datetime

import log_analyzer


finder_test_params = [
    # testname  |  files in dir  |  found log
    (
        'empty dir', [], (None, None)
    ),
    (
        'other files, no logs',
        ['other_file1', 'other_file2'],
        (None, None)
    ),
    (
        'several logs, plain and .gz',
        [
            'nginx-access-ui.log-20170630',
            'nginx-access-ui.log-20181226.gz',
            'nginx-access-ui.log',
            'nginx-access-ui.log-20170630.gz',
            'nginx.log-20190630.gz',
            'not-a-log',
            'nginx-access-ui.log-20200630.bz2',
        ],
        ('nginx-access-ui.log-20181226.gz', datetime.date(2018, 12, 26))
    )
]


parse_line_test_params = [
    # testname  |  line  |  result

    ('bad line', 'some line', None),
    (
        'good line',
        '1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] '
        '"GET /api/v2/banner/1717161 HTTP/1.1" 200 2116 "-" "Slotovod" "-" '
        '"1498697422-2118016444-4708-9752771" "712e90144abee9" 0.138',
        ('/api/v2/banner/1717161', 0.138)
    ),
    (
        'bad time 1',
        '1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] '
        '"GET /api/v2/banner/1717161 HTTP/1.1" 200 2116 "-" "Slotovod" "-" '
        '"1498697422-2118016444-4708-9752771" "712e90144abee9" wrong_time',
        None
    ),
    (
        'bad time 2',
        '1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] '
        '"GET /api/v2/banner/1717161 HTTP/1.1" 200 2116 "-" "Slotovod" "-" '
        '"1498697422-2118016444-4708-9752771" "712e90144abee9" 100.5 -',
        None
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
        self.testdirs.append(testdir)
        for filename in filenames:
            filepath = os.path.join(testdir, filename)
            open(filepath, 'w').close()

        return testdir

    def test_find_latest_log(self):
        for test_name, files_list, result in finder_test_params:
            with self.subTest(test_name=test_name):
                testdir = self._prepare_testdir(files_list)
                found_logfile = log_analyzer.find_latest_log(testdir)
                self.assertEqual(found_logfile, result)


class TestParseLine(unittest.TestCase):
    def test_parse_line(self):
        for test_name, line, result in parse_line_test_params:
            with self.subTest(test_name=test_name):
                self.assertEqual(log_analyzer.parse_one_line(line), result)
