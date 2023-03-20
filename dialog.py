import pandas as pd
import json
from moodle_sync import MoodleSync
import openpyxl
from openpyxl.utils import get_column_letter
import random
from getpass import getpass
from itertools import islice

role_id = 5  # student


def dialog(file):
    if file.endswith(".xlsx"):
        df = read_in_ecxel(file)
    elif file.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        print("Error: File must be .xlsx or .csv. Exiting...")
        exit()
    print(len(df), " Students found")

    ms = login_moodlesync()
    course_id = get_courseid(ms)

    for i, col in enumerate(df.columns):
        print(f"[{i + 1}] {col}")

    choice_column_name = df.columns[get_column_choice("Groupname Column", df)]
    moodleid_column_name = get_moodleid_column_name(df)

    if moodleid_column_name is None:
        email_column_name = df.columns[get_column_choice("Email Column", df)]

        print("Loading student infos from Moodle, please wait...")
        student_info_df = ms.get_enrolled_students(course_id)

        df = df.merge(student_info_df, left_on=email_column_name, right_on="email", how="left")
        moodleid_column_name = "id"

    # show students how are not enrolled
    not_enrolled_df = df[df["id_moo"].isnull()]
    print("\nStudents not enrolled:")
    for i, row in not_enrolled_df.iterrows():
        print(f"\t{row['Schüler']}")

    choice = input("Do you want to enroll them automatically? (y/n): ")
    if choice == "y":
        if moodleid_column_name is None:
            emails = not_enrolled_df["Email"].tolist()
            response = ms.get_user_by_email(emails)
            not_enrolled_ids = [s["id"] for s in response]
        else:
            not_enrolled_ids = df[moodleid_column_name].tolist()
        enrolments = []
        for id in not_enrolled_ids:
            enrolments.append({'roleid': 5, 'userid': id, 'courseid': course_id})  # 5 = student
        # do you want to continue? or stop to enroll them manually
        choice = input(f"Do you want to enroll {len(enrolments)}? (y/n): ")
        if choice == "y":
            r = ms.enroll_students(enrolments)
            # TODO print # of successful enrolments
            print("Loading student infos from Moodle, please wait...")
            student_info_df = ms.get_enrolled_students(course_id)
            df = df.merge(student_info_df, left_on="Email", right_on="email", how="left")
    df = df[df["id_moo"].notnull()]

    # TODO continue here


    # if no continue
    # iter over chosen column and find all needed competences
    needed_competences = []
    for i, value in df2[choice_column_name].iteritems():
        for competence in value.split(";")[:-1]:
            if competence not in needed_competences:
                needed_competences.append(competence)

    needed_competences = sorted(needed_competences)
    print(";".join(needed_competences), " needed competences found.")

    # create groups
    groups = []
    group_ids = {}
    for c in needed_competences:
        group_id = datestring + str(random.randrange(100, 999))
        group_ids[c] = group_id
        groups.append(
            {"courseid": course_id, "name": f'GruppeSYT{c}@{datestring}', "description": "", "idnumber": group_id})

    print("\nCreating groups:")
    print("\t" + "\n\t".join(f"{g['name']} ({g['idnumber']})" for g in groups))
    choice = input("Do you want to continue? (y/n): ")
    if choice == "y":
        response = ms.create_group(groups)

        groupsids = {}
        for g in response:
            groupsids[g["idnumber"]] = g["id"]

        # add students to groups
        members = []
        for c in needed_competences:
            user_ids = df2[df2[choice_column_name].str.contains(c)]["id"].tolist()
            for user_id in user_ids:
                members.append({"groupid": groupsids[group_ids[c]], "userid": user_id})

        choice = input(f"Do you want to add {len(members)} students to {len(needed_competences)} competences? (y/n): ")
        if choice == "y":
            response = ms.add_students_to_group(members)
            print("Done")


def get_moodleid_column_name(df):
    moodleid_column_name = None
    try:
        choice = int(input("Choose Moodle ID Column (or Q for Email Column instead): ")) - 1
        if choice < 0 or choice > len(df.columns):
            print("Invalid input")
            exit()
        moodleid_column_name = df.columns[choice]
    except ValueError:
        pass
    return moodleid_column_name


def get_column_choice(choose_text_string, df):
    try:
        choice = int(input(f"Choose {choose_text_string}: ")) - 1
    except ValueError:
        print("Invalid input")
        exit()
    if choice < 0 or choice > len(df.columns):
        print("Invalid input")
        exit()
    return choice


def get_courseid(ms):
    courses = ms.get_recent_courses()
    for i, course in enumerate(courses.keys()):
        print(f"[{i + 1}] {course}")
    try:
        choice = int(input("Choose a course: ")) - 1
    except ValueError:
        print("Invalid input")
        exit()
    if choice < 0 or choice > len(courses.keys()):
        print("Invalid input")
        exit()
    course_id = list(courses.values())[choice]["id"]
    return course_id


def login_moodlesync():
    credentials_file = input("Enter path to credentials file or 'y' for data/credentials.json: ")
    if credentials_file == "y":
        credentials_file = "data/credentials.json"
    try:
        with open(credentials_file, "r") as f:
            credentials = json.load(f)
    except FileNotFoundError:
        print(f"Error: {credentials_file} not found. Exiting...")
        exit()
    try:
        url = credentials["url"]
        username = credentials["user"]
        password = credentials["password"]
        service = credentials["service"]
    except KeyError:
        print("Error: Invalid credentials file. Exiting...")
        exit()
    try:
        ms = MoodleSync(url, username, password, service)
    except KeyError:
        print("Error: Failed to connect to Server. Exiting...")
        exit()
    return ms


def read_in_ecxel(file):
    try:
        file = openpyxl.load_workbook(file, data_only=True)
    except FileNotFoundError:
        print(f"Error: {file} not found. Exiting...")
        exit()
    for i, sheet in enumerate(file.sheetnames):
        print(f"[{i + 1}] {sheet.title()}")
    try:
        choice = int(input("Choose a sheet: ")) - 1
    except ValueError:
        print("Invalid input")
        exit()
    if choice < 0 or choice > len(file.sheetnames):
        print("Invalid input")
        exit()
    ws = file[file.sheetnames[choice]]
    # iter over first row to find the last interesting column
    # find last column with data
    end_column = ws.max_column + 1
    end_column_letter = get_column_letter(ws.max_column)
    email_column = None
    for cell in ws[1]:
        if cell.value == "Email":
            email_column = cell.column
        if cell.value is None:
            end_column = cell.column
            end_column_letter = cell.column_letter
            break
    # iter over first row to find the last interesting row
    # find last row with data
    end_row = ws.max_row + 1
    for cell in ws["A"]:
        if cell.value is None:
            end_row = cell.row
            break
    data = ws.values
    cols = next(data)[0:end_column - 1]
    data = list(data)
    data = (islice(r, 0, end_column - 1) for r in data[:end_row - 2])
    df = pd.DataFrame(data, columns=cols)
    return df
