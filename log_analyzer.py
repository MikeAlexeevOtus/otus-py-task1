#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import gzip


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

# examples:
# nginx-access-ui.log-20170630.gz
# nginx-access-ui.log-20170630
FILENAME_RE = re.compile(
    r'^nginx-access-ui.log-'
    r'\d{8}'              # yyyyddmm
    r'(\.gz)?$'           # optional .gz extension
)

LOGLINE_RE = re.compile(
    r'^.*?'
    r'"\S+ (\S+)'        # take url from request section, e.g. "GET /api/v2/banner/1717161 HTTP/1.1"
    r'.*'
    r'(\d+(?:\.\d+))$'   # duration
)


def find_latest_log(logdir):
    filenames = os.listdir(logdir)
    log_filenames = [f for f in filenames if FILENAME_RE.match(f)]
    if not log_filenames:
        return

    log_filenames.sort()
    return log_filenames[-1]


def parse_one_line(line):
    match = LOGLINE_RE.match(line)
    if not match:
        return

    url, duration_str = match.groups()
    return url, float(duration_str)


def parse_logfile(log_filepath):
    open_func = open
    if log_filepath.endswith('.gz'):
        open_func = gzip.open

    with open_func(log_filepath, encoding='utf-8') as f:
        for line in f:
            yield parse_one_line(line.strip())


def render_report(template_filepath, output_filepath, stat):
    pass


def calculate_events_stat(events):
    pass


def load_config(config_filepath):
    """validate and load config"""
    pass


def main():
    # argparse, validate and merge configs
    latest_logfile = find_latest_log(logdir)
    # log logfile
    events, errors_percent = parse_logfile(latest_logfile)
    stat = calculate_events_stat(events)
    # limit events
    render_report(template_filepath, output_filepath, stat)


if __name__ == "__main__":
    main()
