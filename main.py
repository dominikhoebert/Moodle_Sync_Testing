import json
import sys
import warnings
from datetime import datetime
import random
from parse_arguments import parse

from loguru import logger
import pandas as pd

from moodle_sync import MoodleSync
from moodle_sync_testing import MoodleSyncTesting
from dialog import dialog


def check_args(args):
    if args.credentials:
        try:
            with open(args.credentials, "r") as f:
                credentials = json.load(f)
        except FileNotFoundError:
            logger.error(f"{args.credentials} not found. Exiting...")
            exit()
        try:
            url = credentials["url"]
            username = credentials["user"]
            password = credentials["password"]
            service = credentials["service"]
        except KeyError:
            logger.error("Invalid credentials file. Exiting...")
            exit()
    elif args.username and args.password and args.url and args.servicename:
        username = args.username
        password = args.password
        url = args.url
        service = args.servicename
    else:
        logger.error("Credentials not provided. Exiting...")
        exit()
    try:
        ms = MoodleSync(url, username, password, service)
    except KeyError:
        logger.error("Failed to connect to Server. Exiting...")
        exit()
    try:
        if args.file.endswith(".xlsx"):
            if args.sheet.isdigit():
                student_df = pd.read_excel(args.file, sheet_name=int(args.sheet))
            else:
                student_df = pd.read_excel(args.file, sheet_name=args.sheet)
        elif args.file.endswith(".csv"):
            student_df = pd.read_csv(args.file)
    except FileNotFoundError:
        logger.error(f"{args.file} not found. Exiting...")
        exit()
    except (KeyError, ValueError):
        logger.error("Invalid sheet name. Exiting...")
        exit()
    if not (args.course_id and args.col_name and args.group_col):
        logger.error("Missing Column arguments. Exiting...")
        exit()
    logger.info(f"{len(student_df)} students found in {args.file}")
    moodle_sync = MoodleSyncTesting(url, username, password, service, args.course_id, student_df, args.col_name,
                                    args.group_col)
    return moodle_sync


def moodle_sync_workflow(args, moodle_sync):  # TODO Logging!
    moodle_sync.join_enrolled_students()
    if args.add_students:
        moodle_sync.enroll_students_for_groups()
        moodle_sync.join_enrolled_students()
    moodle_sync.clean_students()
    for g in moodle_sync.group_names:
        logger.info(f"Creating group {g}")
    if args.preview:
        ...  # TODO
    else:
        moodle_sync.create_groups()
        moodle_sync.add_students_to_groups()


def main():
    warnings.simplefilter("ignore")

    args = parse()
    logger.add("logs/moodle_sync_testing.log", rotation="50 MB", level="INFO")

    if args.no_output:
        logger.disable("__main__")

    logger.info(f"Arguments: {args}")

    if args.dialog:
        dialog(args.file)
        exit()

    moodle_sync = check_args(args)
    moodle_sync_workflow(args, moodle_sync)


if __name__ == "__main__":
    main()
