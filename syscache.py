#!/usr/bin/python
"""Script to parse Syscache.hve"""

from yarp import Registry
from datetime import datetime as dt

import argparse
import csv
import os
import struct
import sys

# Code Reference for FILETIME to Python Date:
# https://gist.github.com/Mostafa-Hamdy-Elgiar/9714475f1b3bc224ea063af81566d873
EPOCH_AS_FILETIME = 116444736000000000   # January 1, 1970 as MS FILETIME
HUNDREDS_OF_NANOSECONDS = 10000000


def _validate_input(options):
    if options.hive is None:
        print("No registry hive provided!")
        return False
    elif not os.path.isfile(options.hive):
        print("Path of registry hive is invalid!")
        return False

    if not os.path.isdir(options.output):
        print("Path of output directory is invalid!")

    return True


def decode_fileid(file_id):
    mft_rec1, mft_rec2, mft_seq = struct.unpack('IHH', bytearray(file_id))
    return mft_rec1 | (mft_rec2 << 16), mft_seq


def parse_values(yhive, output_path):
    object_id = object_lru = file_id = usn = usn_id = 0
    file_ref = [0, 0]
    usn_id_timestamp = sha1 = aeprogram_id = ''

    with open(output_path, mode='w', newline='') as outfile:
        entry_writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        entry_writer.writerow(['_ObjectId_', '_ObjectLru_', '_FileId_', 'MFT Rec No.', 'MFT Seq No.', '_Usn_',
                               '_UsnJournalId_', 'UsnJournalId_Timestamp', 'Last Write Timestamp', 'AeFileID',
                               'AeProgramID'])
        key = yhive.find_key('DefaultObjectStore\\ObjectTable')
        for sk in key.subkeys():
            for v in sk.values():
                if v.name() == '_ObjectId_':
                    object_id = v.data()
                if v.name() == '_ObjectLru_':
                    object_lru = v.data()
                if v.name() == '_FileId_':
                    file_id = v.data()
                    file_ref = decode_fileid(v.data_raw())
                if v.name() == '_Usn_':
                    usn = v.data()
                if v.name() == '_UsnJournalId_':
                    usn_id = v.data()
                    usn_id_timestamp = dt.utcfromtimestamp((usn_id - EPOCH_AS_FILETIME) / HUNDREDS_OF_NANOSECONDS)
                if v.name() == 'AeFileID':
                    sha1 = v.data().decode('ascii').replace('\0', '')[4:]
                if v.name() == 'AeProgramID':
                    aeprogram_id = v.data().decode('ascii').replace('\0', '')
            entry_writer.writerow([object_id, object_lru, file_id, file_ref[0], file_ref[1], usn, usn_id,
                                   usn_id_timestamp, sk.last_written_timestamp(), sha1, aeprogram_id])


def main():
    start_time = dt.now()
    timestamp = dt.now().strftime("%Y-%m-%d@%H%M%S")

    argument_parser = argparse.ArgumentParser(description=(
        "syscache parses values of subkeys under Syscache\DefaultObjectStore\\ObjectTable"
    ))

    argument_parser.add_argument('-f', '--hive', default=None, help="path of the registry hive to be parsed")
    argument_parser.add_argument('-o', '--output', default=None, help=(
        "path to the directory to store the output, default to directory of the registry hive"))

    options = argument_parser.parse_args()
    if options.hive is not None:
        options.hive = os.path.abspath(options.hive)
    if options.output is None:
        options.output = os.path.dirname(options.hive)  # default to directory of the registry hive
    else:
        options.output = os.path.abspath(options.output)

    if not _validate_input(options):
        sys.exit(1)

    hive_name = os.path.basename(options.hive)
    output_path = os.path.join(options.output, hive_name + '_' + timestamp + '.csv')
    with open(options.hive, 'rb') as hive:
        yarp_hive = Registry.RegistryHive(hive)
        parse_values(yarp_hive, output_path)

    print("\rTime Taken: {}".format(dt.now() - start_time))


if __name__ == '__main__':
    if not main():
        sys.exit(1)
    else:
        sys.exit(0)
