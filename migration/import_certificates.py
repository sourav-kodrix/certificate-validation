from openpyxl import load_workbook
from datetime import datetime
import os
import requests


# ==============================
# Configuration
# ==============================

EXCEL_FILE = "Certificate Verification Data Trivandrum.xlsx"

API_URL = os.getenv(
    "CERTIFICATE_API_URL",
    "http://192.168.56.100/api/certificates"
)

API_KEY = os.getenv("CERTIFICATE_API_KEY")

# Safety switch
DRY_RUN = True


REQUIRED_COLUMNS = [
    "Student Name",
    "Student/Registration ID",
    "Course/Program",
    "Batch",
    "Certificate ID/Certificate Number",
    "Certificate Issued Date",
    "Branch",
]


# ==============================
# Check API Key
# ==============================

if not API_KEY:
    print("\nERROR: CERTIFICATE_API_KEY environment variable is not set.")
    print("Migration stopped.")
    raise SystemExit(1)


# ==============================
# Helper functions
# ==============================

def clean_string(value):
    """
    Convert a cell value to a clean string.
    """
    if value is None:
        return ""

    return str(value).strip()


def format_date(value):
    """
    Convert Excel date into YYYY-MM-DD format.
    Supports Excel date values and text dates
    such as 06/11/2025, 06-11-2025, and 04-07-26.
    """

    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")

    if value is None:
        return ""

    value = str(value).strip()

    if not value:
        return ""

    for date_format in ("%d/%m/%Y", "%d-%m-%Y", "%d-%m-%y", "%d/%m/%y"):
        try:
            parsed_date = datetime.strptime(value, date_format)
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return value


# ==============================
# Load Excel
# ==============================

try:
    workbook = load_workbook(
        EXCEL_FILE,
        data_only=True
    )
except Exception as error:
    print(f"\nERROR: Could not open Excel file: {error}")
    raise SystemExit(1)


sheet = workbook.active


print("\n========================================")
print("CERTIFICATE DATA MIGRATION")
print("========================================")

print(f"\nExcel sheet: {sheet.title}")
print(f"API URL: {API_URL}")


# ==============================
# Read headers
# ==============================

headers = [
    sheet.cell(row=1, column=column).value
    for column in range(1, 8)
]

print("\nExcel columns:")

for index, header in enumerate(headers, start=1):
    print(f"{index}. {header}")


# ==============================
# Check headers
# ==============================

if headers != REQUIRED_COLUMNS:

    print("\nERROR: Excel columns do not match expected columns.")

    print("\nExpected:")
    for column in REQUIRED_COLUMNS:
        print(f"- {column}")

    print("\nFound:")
    for column in headers:
        print(f"- {column}")

    raise SystemExit(1)


print("\nColumn structure: OK")


# ==============================
# Process records
# ==============================

valid_records = []
invalid_records = []

student_ids = {}
certificate_ids = {}

total_rows = 0


for row_number in range(2, sheet.max_row + 1):

    # Read first 7 cells
    row_values = [
        sheet.cell(row=row_number, column=column).value
        for column in range(1, 8)
    ]

    # Skip completely empty rows
    if all(value is None for value in row_values):
        continue

    total_rows += 1

    # --------------------------------
    # Read Excel values
    # --------------------------------

    student_name = sheet.cell(row=row_number, column=1).value
    student_id = sheet.cell(row=row_number, column=2).value
    course = sheet.cell(row=row_number, column=3).value
    batch = sheet.cell(row=row_number, column=4).value
    certificate_id = sheet.cell(row=row_number, column=5).value
    issued_date = sheet.cell(row=row_number, column=6).value
    branch = sheet.cell(row=row_number, column=7).value

    # --------------------------------
    # Clean values
    # --------------------------------

    student_name = clean_string(student_name)
    student_id = clean_string(student_id)
    course = clean_string(course)
    batch = clean_string(batch)
    certificate_id = clean_string(certificate_id)
    branch = clean_string(branch)

    issued_date = format_date(issued_date)

    # --------------------------------
    # Validation
    # --------------------------------

    errors = []

    if not student_name:
        errors.append("Student name is missing")

    if not student_id:
        errors.append("Student ID is missing")

    if not course:
        errors.append("Course is missing")

    if not batch:
        errors.append("Batch is missing")

    if not certificate_id:
        errors.append("Certificate ID is missing")

    if not issued_date:
        errors.append("Issued date is missing")

    if not branch:
        errors.append("Branch is missing")

    # --------------------------------
    # Check duplicate Student ID
    # --------------------------------

    if student_id:

        if student_id in student_ids:

            errors.append(
                f"Duplicate Student ID "
                f"(also found in row {student_ids[student_id]})"
            )

        else:
            student_ids[student_id] = row_number

    # --------------------------------
    # Check duplicate Certificate ID
    # --------------------------------

    if certificate_id:

        if certificate_id in certificate_ids:

            errors.append(
                f"Duplicate Certificate ID "
                f"(also found in row {certificate_ids[certificate_id]})"
            )

        else:
            certificate_ids[certificate_id] = row_number

    # --------------------------------
    # Create mapped record
    # --------------------------------

    record = {
        "studentName": student_name,
        "studentId": student_id,
        "course": course,
        "batch": batch,
        "certificateId": certificate_id,
        "issuedDate": issued_date,
        "branch": branch,
    }

    # --------------------------------
    # Store valid / invalid records
    # --------------------------------

    if errors:

        invalid_records.append({
            "row": row_number,
            "errors": errors,
            "data": record,
        })

    else:

        valid_records.append(record)


# ==============================
# Validation Summary
# ==============================

print("\n========================================")
print("VALIDATION SUMMARY")
print("========================================")

print(f"\nTotal records: {total_rows}")
print(f"Valid records: {len(valid_records)}")
print(f"Invalid records: {len(invalid_records)}")

print(
    f"Duplicate Student IDs: "
    f"{total_rows - len(set(student_ids.keys()))}"
)

print(
    f"Duplicate Certificate IDs: "
    f"{total_rows - len(set(certificate_ids.keys()))}"
)


# ==============================
# Show invalid records
# ==============================

if invalid_records:

    print("\n========================================")
    print("INVALID RECORDS")
    print("========================================")

    for item in invalid_records:

        print(f"\nExcel Row: {item['row']}")

        for error in item["errors"]:
            print(f"  - {error}")

        print("  Data:")
        print(f"    {item['data']}")


# ==============================
# Show sample records
# ==============================

print("\n========================================")
print("SAMPLE VALID RECORDS")
print("========================================")

for index, record in enumerate(valid_records[:5], start=1):

    print(f"\nRecord {index}:")

    for key, value in record.items():
        print(f"  {key}: {value}")


# ==============================
# Stop if validation failed
# ==============================

if invalid_records:
    print("\n========================================")
    print("INVALID RECORDS")
    print("========================================")
    print(f"\n{len(invalid_records)} invalid records found.")
    print("These records will be skipped.")
    print("The valid records will continue to migration.")


# ==============================
# Migration
# ==============================

# ==============================
# Migration
# ==============================

if DRY_RUN:

    print("\n========================================")
    print("DRY RUN MODE")
    print("========================================")

    print(f"\nRecords that would be migrated: {len(valid_records)}")
    print(f"Records that would be skipped: {len(invalid_records)}")

    print("\nNo API requests will be made.")
    print("No data will be inserted into MongoDB.")

else:

    print("\n========================================")
    print("STARTING MIGRATION")
    print("========================================")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    migrated_count = 0
    skipped_count = 0
    failed_count = 0

    failed_records = []

    for index, record in enumerate(valid_records, start=1):

        print(
            f"\n[{index}/{len(valid_records)}] "
            f"Migrating: {record['certificateId']}"
        )

        try:

            response = requests.post(
                API_URL,
                json=record,
                headers=headers,
                timeout=15,
            )

            if response.status_code == 201:

                migrated_count += 1

                print("  SUCCESS: Certificate migrated.")

            elif response.status_code == 409:

                skipped_count += 1

                print(
                    "  SKIPPED: Certificate already exists."
                )

            elif response.status_code == 401:

                print(
                    "\nERROR: API authentication failed."
                )

                print(
                    "Check CERTIFICATE_API_KEY."
                )

                print("\nMigration stopped.")

                raise SystemExit(1)

            else:

                failed_count += 1

                try:
                    error_data = response.json()
                except Exception:
                    error_data = response.text

                print(
                    f"  FAILED: HTTP {response.status_code}"
                )

                print(
                    f"  Response: {error_data}"
                )

                failed_records.append({
                    "certificateId": record["certificateId"],
                    "studentId": record["studentId"],
                    "status": response.status_code,
                    "response": error_data,
                })

        except requests.exceptions.RequestException as error:

            failed_count += 1

            print(
                f"  FAILED: Request error: {error}"
            )

            failed_records.append({
                "certificateId": record["certificateId"],
                "studentId": record["studentId"],
                "status": "REQUEST_ERROR",
                "response": str(error),
            })

    # ==============================
    # Migration Summary
    # ==============================

    print("\n========================================")
    print("MIGRATION SUMMARY")
    print("========================================")

    print(f"\nTotal Excel records: {total_rows}")
    print(f"Valid records: {len(valid_records)}")
    print(f"Invalid records: {len(invalid_records)}")
    print(f"Successfully migrated: {migrated_count}")
    print(f"Already existed / skipped: {skipped_count}")
    print(f"Failed: {failed_count}")

    if failed_records:

        print("\n========================================")
        print("FAILED MIGRATIONS")
        print("========================================")

        for item in failed_records:

            print(f"\nCertificate ID: {item['certificateId']}")
            print(f"Student ID: {item['studentId']}")
            print(f"Status: {item['status']}")
            print(f"Response: {item['response']}")

    print("\n========================================")

    if failed_count == 0:
        print("MIGRATION COMPLETED SUCCESSFULLY")
    else:
        print("MIGRATION COMPLETED WITH ERRORS")

    print("========================================")


