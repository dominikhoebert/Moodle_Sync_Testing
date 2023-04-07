import json
import warnings
from datetime import datetime
import random
from parse_arguments import parse

from loguru import logger
import pandas as pd

from moodle_sync import MoodleSync
from dialog import dialog

logger.add("logs/moodle_sync_testing.log", rotation="50 MB", level="INFO")

if __name__ == "__main__":
    warnings.simplefilter("ignore")

    args = parse()
    logger.info(f"Arguments: {args}")

    if args.dialog:
        dialog(args.file)
        exit()

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

    if not (args.course_id and (args.moodleid_col or args.email_col) and args.group_col):
        logger.error("Missing Column arguments. Exiting...")
        exit()

    logger.info(f"{len(student_df)} students found in {args.file}")
    student_info_df = ms.get_enrolled_students(args.course_id)

    if args.moodleid_col:
        moodle_id_column_name = args.moodleid_col
        email_column_name = None
        student_df_merged = student_df.merge(student_info_df, left_on=moodle_id_column_name, right_on="id_joined", how="left")
    elif args.email_col:
        email_column_name = args.email_col
        student_df_merged = student_df.merge(student_info_df, left_on=email_column_name, right_on="email_joined", how="left")
        moodle_id_column_name = "id_joined"

    group_column_name = args.group_col

    if args.add_students:
        not_enrolled_df = student_df_merged[student_df_merged["id_joined"].isnull()]
        if len(not_enrolled_df) > 0:
            for index, row in not_enrolled_df.iterrows():
                logger.info(f"Adding {row} to course")
            if email_column_name is not None:
                emails = not_enrolled_df[email_column_name].tolist()
                response = ms.get_user_by_email(emails)
                not_enrolled_ids = [s["id"] for s in response]
            else:
                not_enrolled_ids = not_enrolled_df[moodle_id_column_name].tolist()
            enrolments = []
            for id in not_enrolled_ids:
                enrolments.append({'roleid': 5, 'userid': id, 'courseid': args.course_id})  # 5 = student
            r = ms.enroll_students(enrolments)
            student_info_df = ms.get_enrolled_students(args.course_id)
            if email_column_name:
                student_df_merged = student_df.merge(student_info_df, left_on=email_column_name, right_on="email_joined", how="left")
            else:
                student_df_merged = student_df.merge(student_info_df, left_on=moodle_id_column_name, right_on="id_joined", how="left")

    student_df_merged = student_df_merged[student_df_merged["id_joined"].notnull()]
    student_df_merged = student_df_merged[student_df_merged[group_column_name].notnull()]
    student_df_merged = student_df_merged[student_df_merged[group_column_name] != ""]

    group_names = student_df_merged[group_column_name].unique()
    for g in group_names:
        logger.info(f"Creating group {g}")

    # create groups
    groups = []
    group_ids = {}
    date_string = datetime.now().strftime("%Y%m%d")
    for g in group_names:
        group_id = date_string + str(random.randrange(100, 999))
        group_ids[g] = group_id
        groups.append(
            {"courseid": args.course_id, "name": g, "description": "", "idnumber": group_id})

    response = ms.create_group(groups)
    groups_ids = {}
    for g in response:
        groups_ids[g["idnumber"]] = g["id"]

    # add students to groups
    members = []
    for g in group_names:
        logger.info(f"Adding students to group {g}:")
        for row in student_df_merged[student_df_merged[group_column_name] == g].iterrows():
            logger.info(f"  {row}")
            members.append({"groupid": groups_ids[group_ids[g]], "userid": row[moodle_id_column_name]})

    if args.preview is False:
        response = ms.add_students_to_group(members)