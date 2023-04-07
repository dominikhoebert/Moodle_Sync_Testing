import pandas as pd
import json
from moodle_sync import MoodleSync
import warnings
from parse_arguments import parse
from dialog import dialog

if __name__ == "__main__":
    warnings.simplefilter("ignore")

    args = parse()

    if args.dialog:
        dialog(args.file)
        exit()

    if args.credentials:
        try:
            with open(args.credentials, "r") as f:
                credentials = json.load(f)
        except FileNotFoundError:
            print(f"Error: {args.credentials} not found. Exiting...")
            exit()
        try:
            url = credentials["url"]
            username = credentials["user"]
            password = credentials["password"]
            service = credentials["service"]
        except KeyError:
            print("Error: Invalid credentials file. Exiting...")
            exit()
    elif args.username and args.password and args.url and args.servicename:
        username = args.username
        password = args.password
        url = args.url
        service = args.servicename
    else:
        print("Error: Credentials not provided. Exiting...")
        exit()
    try:
        ms = MoodleSync(url, username, password, service)
    except KeyError:
        print("Error: Failed to connect to Server. Exiting...")
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
        print(f"Error: {args.file} not found. Exiting...")
        exit()
    except (KeyError, ValueError):
        print("Error: Invalid sheet name. Exiting...")
        exit()

    if not (args.course_id and (args.moodleid_col or args.email_col) and args.group_col):
        print("Error: Missing Column arguments. Exiting...")
        exit()

    student_info_df = ms.get_enrolled_students(args.course_id)

    if args.moodleid_col:
        moodle_id_column_name = args.moodleid_col
        email_column_name = None
        df2 = student_df.merge(student_info_df, left_on=moodle_id_column_name, right_on="id_joined", how="left")
    elif args.email_col:
        email_column_name = args.email_col
        df2 = student_df.merge(student_info_df, left_on=email_column_name, right_on="email_joined", how="left")
        moodle_id_column_name = None

    group_column_name = args.group_col

    if args.add_students:
        ...
