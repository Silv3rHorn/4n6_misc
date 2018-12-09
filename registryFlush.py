#!/usr/bin/python
"""Script to flush transaction log files into their corresponding registry hives"""

from yarp import Registry
from datetime import datetime as dt

import argparse
import os
import sys

LOG_PATH = [None, None, None]


def _validate_input(options, hive_name):
    global LOG_PATH

    if options.hive is None:
        print("No registry hive provided!")
        return False
    elif not os.path.isfile(options.hive):
        print("Path of registry hive is invalid!")
        return False

    if not os.path.isdir(options.output):
        print("Path of output directory is invalid!")

    LOG_PATH[0] = os.path.join(options.logs, hive_name + '.LOG')
    LOG_PATH[1] = os.path.join(options.logs, hive_name + '.LOG1')
    LOG_PATH[2] = os.path.join(options.logs, hive_name + '.LOG2')

    # check if each transaction log exists
    for idx in range(len(LOG_PATH)):
        if not os.path.isfile(LOG_PATH[idx]):
            LOG_PATH[idx] = None

    # if log path is invalid or no transaction logs at log path exists
    if not os.path.isdir(options.logs) or (LOG_PATH[0] is None and LOG_PATH[1] is None and LOG_PATH[2] is None):
        print("Path of transaction logs is invalid!")
        return False

    return True


def main():
    start_time = dt.now()
    timestamp = dt.now().strftime("%Y-%m-%d@%H%M%S")

    argument_parser = argparse.ArgumentParser(description=(
        "registryFlush flushes transaction log files into their corresponding registry hive"
    ))

    argument_parser.add_argument('-f', '--hive', default=None, help="path of the registry hive to be flushed")
    argument_parser.add_argument('-l', '--logs', default=None, help=(
        "path of corresponding transaction log files, default to directory of the registry hive"))
    argument_parser.add_argument('-o', '--output', default=None, help=(
        "path to the directory to store the output, default to directory of the registry hive"))
    argument_parser.add_argument('--overwrite', action='store_true', help="overwrite existing hive")

    options = argument_parser.parse_args()
    if options.hive is not None:
        options.hive = os.path.abspath(options.hive)
    if options.logs is None:
        options.logs = os.path.dirname(options.hive)  # default to directory of the registry hive
    else:
        options.logs = os.path.abspath(options.logs)
    if options.output is None:
        options.output = os.path.dirname(options.hive)    # default to directory of the registry hive
    else:
        options.output = os.path.abspath(options.output)
    hive_name = os.path.basename(options.hive)

    if not _validate_input(options, hive_name):
        sys.exit(1)

    with open(options.hive, 'rb') as hive:
        yarp_hive = Registry.RegistryHive(hive)

        log = []
        for path in LOG_PATH:
            if path is None:
                log.append(None)
            else:
                log.append(open(path, 'rb'))

        result = yarp_hive.recover_auto(log[0], log[1], log[2])

    if result.recovered:
        print("Flush succeeded!")

        if options.overwrite:
            outfile = os.path.join(options.output, hive_name)
            if os.path.isfile(outfile):
                os.rename(outfile, outfile + '.old')  # backup original file
        else:
            outfile = os.path.join(options.output, hive_name + '_' + timestamp)

        yarp_hive.save_recovered_hive(outfile)
    elif not result.recovered:
        print("Flush failed!")
    if result.is_new_log is None:
        print("Log files does not contain new data!")

    for file in log:
        if file is not None:
            file.close()
    print("\rTime Taken: {}".format(dt.now() - start_time))


if __name__ == '__main__':
    if not main():
        sys.exit(1)
    else:
        sys.exit(0)
