#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict, namedtuple
from string import Template
import argparse
import copy
import datetime
import json
import gzip
import logging
import os
import pathlib
import re
import statistics
import sys


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

CONFIG = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "ERRORS_THRESHOLD": 0.1,
}

# examples:
# nginx-access-ui.log-20170630.gz
# nginx-access-ui.log-20170630
FILENAME_RE = re.compile(
    r'^nginx-access-ui.log-'
    r'(\d{8})'              # yyyyddmm
    r'(?:\.gz)?$'           # optional .gz extension
)

LOGLINE_RE = re.compile(
    r'^.*?'
    r'"\S+ (\S+) HTTP/.+"'     # take url from request section, e.g. "GET /api/v2/banner/1717161 HTTP/1.1"
    r'.*'
    r'(\d+(?:\.\d+))$'         # duration, integer or float
)

StatEntry = namedtuple(
    'StatEntry',
    'url count count_perc time_sum time_perc time_avg time_max time_med'
)


TEMPLATE_FILEPATH = os.path.join(
    os.path.dirname(__file__),
    'report.html'
)


def find_latest_log(logdir):
    latest_log = None
    latest_date = None

    for filename in os.listdir(logdir):
        match = FILENAME_RE.match(filename)
        if not match:
            continue

        date_str = match.group(1)
        date = datetime.datetime.strptime(date_str, '%Y%m%d').date()
        if not latest_date or date > latest_date:
            latest_date = date
            latest_log = filename

    return latest_log, latest_date


def parse_one_line(line):
    match = LOGLINE_RE.match(line)
    if not match:
        return

    url, duration_str = match.groups()
    return url, float(duration_str)


def parse_logfile(log_filepath, errors_threshold):
    errors_count = 0
    total_lines = 0
    open_func = open

    if log_filepath.endswith('.gz'):
        open_func = gzip.open

    with open_func(log_filepath, mode='rt', encoding='utf-8') as f:
        for line in f:
            total_lines += 1
            parse_result = parse_one_line(line.strip())
            if parse_result is None:
                errors_count += 1
                continue
            yield parse_result

    errors_ratio = errors_count / total_lines
    if errors_ratio > errors_threshold:
        raise RuntimeError(f'too many errors, errors ratio: {errors_ratio}'))


def render_report(template_filepath, output_filepath, stat_entries, limit):
    stat_entries = sorted(stat_entries, key=lambda x: x.time_sum, reverse=True)
    stat_entries = stat_entries[:limit]

    table_json = [dict(entry._asdict()) for entry in stat_entries]

    with open(template_filepath, encoding='utf-8') as template_file:
        template_data = template_file.read()
    template = Template(template_data)

    with open(output_filepath, 'w', encoding='utf-8') as output_file:
        output_file.write(
            template.safe_substitute({'table_json': table_json})
        )


def calculate_events_stat(events):
    total_duration = 0
    total_count = 0
    url_durations = defaultdict(list)
    for url, duration in events:
        total_count += 1
        total_duration += duration
        url_durations[url].append(duration)

    stat_entries = []
    for url, durations in url_durations.items():
        durations.sort()
        count = len(durations)
        time_sum = sum(durations)
        time_max = durations[-1] if durations else 0

        stat_entry = StatEntry(
            url=url,
            count=count,
            count_perc=count / total_count,
            time_sum=time_sum,
            time_perc=time_sum / total_duration,
            time_avg=time_sum / count,
            time_max=time_max,
            time_med=statistics.median(durations) if durations else 0
        )

        stat_entries.append(stat_entry)

    return stat_entries


def load_config(config_filepath):
    """validate and load config"""
    if not config_filepath.exists():
        raise RuntimeError(f'config file "{config_filepath}" doesn\'t exist')

    with open(config_filepath) as f:
        try:
            return json.load(f)
        except ValueError:
            raise RuntimeError(f'config file "{config_filepath}" is not a valid json file')


def make_output_report_path(report_dir, date):
    filename = 'report-{}.html'.format(date.strftime('%Y.%m.%d'))
    return os.path.join(report_dir, filename)


def main(base_config):
    config = copy.deepcopy(base_config)
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '--config', '-c', required=False, type=pathlib.Path,
        help='Path to config json file'
    )
    args = arg_parser.parse_args()
    if args.config:
        config.update(load_config(args.config))

    logging.basicConfig(
        filename=config.get('LOG'),
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S',
        level=logging.DEBUG if config.get('DEBUG') else logging.INFO
    )

    logging.debug('using config: %s', config)
    logdir = config['LOG_DIR']
    if not os.path.exists(logdir):
        raise RuntimeError(f'logdir "{logdir}" doesn\'t exist')

    latest_logfile, date = find_latest_log(logdir)
    if not latest_logfile:
        logging.error('not found log for processing')
        return

    logging.info('found latest log for processing: %s', latest_logfile)

    output_filepath = make_output_report_path(config['REPORT_DIR'], date)
    if os.path.exists(output_filepath):
        logging.info('report %s already exists, skip processing', output_filepath)
        return

    logging.info('writing report to %s', output_filepath)
    os.makedirs(config['REPORT_DIR'], exist_ok=True)
    events = parse_logfile(os.path.join(logdir, latest_logfile),
                           config['ERRORS_THRESHOLD'])
    stat_entries = calculate_events_stat(events)
    render_report(TEMPLATE_FILEPATH, output_filepath, stat_entries, config['REPORT_SIZE'])
    logging.info('processing done')


if __name__ == "__main__":
    try:
        main(CONFIG)
    except Exception:
        logging.exception('failed to process log')
        sys.exit(1)
