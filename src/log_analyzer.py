#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def find_latest_log(logdir):
    pass


def parse_logfile(logfile):
    """return list of pairs (url, request time) and percent of not parsed lines"""
    pass


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
