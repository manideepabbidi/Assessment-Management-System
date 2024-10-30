from google.cloud import firestore, storage, bigquery
import json
def fetch_students_data():
    # Initialize Firestore client
    firestore_client = firestore.Client()

    # Fetch data from Firestore students collection
    students_ref = firestore_client.collection('students')
    student_data = [doc.to_dict() for doc in students_ref.stream()]
    #print(student_data)
    return student_data

def fetch_submissions_data(bucket_name, folder_path):
    # Initialize GCS client
    storage_client = storage.Client()

    # Fetch data from the GCS bucket
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=folder_path)
    
    submission_data = []
    for blob in blobs:
        # Download blob content as byte string
        content = blob.download_as_string()

        # Convert byte string to dictionary (assuming it's in JSON format)
        submission_dict = json.loads(content.decode('utf-8'))

        # Append dictionary to submission_data list
        submission_data.append(submission_dict)
    #print(submission_data)
    return submission_data

def insert_students_data(project_id, dataset_id, table_id, student_data):
    # Initialize BigQuery client
    bq_client = bigquery.Client()

    # Get BigQuery table reference
# Add more fields as needed


    
    
    table_ref = bq_client.dataset(dataset_id).table(table_id)

    # Insert data into the table
    errors = bq_client.insert_rows_json(table_ref, student_data)

    if not errors:
        print(f"Data inserted into BigQuery table {table_id}.")
    else:
        print("Errors occurred while inserting data into BigQuery table:", errors)

def insert_submissions_data(project_id, dataset_id, table_id, submission_data):
    # Initialize BigQuery client
    bq_client = bigquery.Client()

    # Get BigQuery table reference
    
    table_ref = bq_client.dataset(dataset_id).table(table_id)
    unique_submission_data = []
    seen_submission_ids = set()
    for submission in submission_data:
        submission_id = submission.get("id")  # Assuming "id" is the unique identifier
        if submission_id not in seen_submission_ids:
            unique_submission_data.append(submission)
            seen_submission_ids.add(submission_id)
    # Insert data into the table
    errors = bq_client.insert_rows_json(table_ref, unique_submission_data)

    if not errors:
        print(f"Data inserted into BigQuery table {table_id}.")
    else:
        print("Errors occurred while inserting data into BigQuery Submissions table:", errors)
def create_table_if_not_exists(dataset_id, table_id, schema):
    # Initialize BigQuery client
    bq_client = bigquery.Client()

    # Get BigQuery dataset reference
    dataset_ref = bq_client.dataset(dataset_id)

    # Construct the table reference
    table_ref = dataset_ref.table(table_id)

    # Check if the table exists
    #table = bq_client.get_table(table_ref)
    table = bigquery.Table(table_ref, schema=schema)
    bq_client.create_table(table)
    print(f"Table {table_id} created in dataset {dataset_id}.")


# Usage example


# Example usage:
if __name__ == "__main__":
    project_id = "sams-420304"
    dataset_id = "test_db"
    bucket_name = "test_bucket_sams"
    folder_path = "submissions"

# Fetch data from Firestore students collection
    student_data = fetch_students_data()

# Fetch data from the GCS bucket
    submission_data = fetch_submissions_data(bucket_name, folder_path)

# Insert student data into BigQuery
    insert_students_data(project_id, dataset_id, "students", student_data)

# Insert submission data into BigQuery
    insert_submissions_data(project_id, dataset_id, "submissions", submission_data)
