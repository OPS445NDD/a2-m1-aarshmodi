#!/usr/bin/env python3

'''
OPS445 Assignment 2 - Summer 2026
Program: assignment2.py
Author: Aarsh Modi

The python code in this file is original work written by
Aarsh Modi. No code in this file is copied from any other source
except those provided by the course instructor, including any person,
textbook, or online resource. I have not shared this python script
with anyone or anything except for submission for grading.
I understand that the Academic Honesty Policy will be enforced and
violators will be reported and appropriate action will be taken.

Description: Displays system memory usage and optionally memory usage
of a specified program.

Date: July 2026

'''

import argparse
import os
import sys


def parse_command_args() -> object:
    parser = argparse.ArgumentParser(
        description="Memory Visualiser -- See Memory Usage Report with bar charts",
        epilog="Copyright 2023"
    )

    parser.add_argument(
        "-l",
        "--length",
        type=int,
        default=20,
        help="Specify the length of the graph. Default is 20."
    )

    parser.add_argument(
        "-H",
        "--human-readable",
        action="store_true",
        help="Print sizes in human readable format."
    )

    parser.add_argument(
        "program",
        type=str,
        nargs='?',
        help="If specified, show memory use of all associated processes."
    )

    return parser.parse_args()


def percent_to_graph(percent: float, length: int = 20) -> str:
    bars = int(percent * length)
    return "#" * bars + " " * (length - bars)


def get_sys_mem() -> int:
    "return total system memory (used or available) in kB"
    with open('/proc/meminfo', 'r') as f:
        for line in f:
            if line.startswith('MemTotal'):
                return int(line.split()[1])

def get_avail_mem() -> int:
    "return total memory that is currently available"
    with open('/proc/meminfo', 'r') as f:
        for line in f:
            if line.startswith('MemAvailable'):
                return int(line.split()[1])


def pids_of_prog(app_name: str) -> list:
    try:
        output = os.popen(f"pidof {app_name}").read().strip()
        if output == "":
            return []
        return output.split()
    except:
        return []


def rss_mem_of_pid(proc_id: str) -> int:
    rss = 0
    try:
        with open(f"/proc/{proc_id}/smaps") as f:
            for line in f:
                if line.startswith("Rss:"):
                    rss += int(line.split()[1])
    except:
        return 0
    return rss


def bytes_to_human_r(kibibytes: int, decimal_places: int = 2) -> str:
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']
    suf_count = 0
    result = float(kibibytes)

    while result >= 1024 and suf_count < len(suffixes) - 1:
        result /= 1024
        suf_count += 1

    return f"{result:.{decimal_places}f} {suffixes[suf_count]}"


if __name__ == "__main__":
    args = parse_command_args()

    total = get_sys_mem()
    available = get_avail_mem()
    used = total - available
    percent = used / total

    if args.human_readable:
        used_display = bytes_to_human_r(used)
        total_display = bytes_to_human_r(total)
    else:
        used_display = f"{used} KiB"
        total_display = f"{total} KiB"

    print(f"System Memory Usage: {used_display} / {total_display}")
    print(f"[{percent_to_graph(percent, args.length)}] {percent:.1%}")

    if args.program:
        pids = pids_of_prog(args.program)

        if not pids:
            print(f"\nNo running process named '{args.program}'")
            sys.exit(1)

        total_rss = 0

        print(f"\nMemory usage for '{args.program}':")

        for pid in pids:
            rss = rss_mem_of_pid(pid)
            total_rss += rss

            if args.human_readable:
                mem = bytes_to_human_r(rss)
            else:
                mem = f"{rss} KiB"

            print(f"PID {pid}: {mem}")

        if args.human_readable:
            total_mem = bytes_to_human_r(total_rss)
        else:
            total_mem = f"{total_rss} KiB"

        print(f"Total RSS: {total_mem}")
