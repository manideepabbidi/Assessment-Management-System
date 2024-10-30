# assessment/gcp_utils.py

from google.cloud import storage, firestore, pubsub_v1
from google.cloud import bigquery
import os
import pandas as pd
import datetime
from google.cloud import functions_v1
from google.cloud import aiplatform

# Set the environment variable for GCP service account key file
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Nandu/OneDrive/Documents/Assessment_project/assessment_management_gcp/assessment/sams-key2.json'

def upload_to_cloud_storage(file_path, bucket_name, destination_blob_name):
    """Uploads a file to Google Cloud Storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(file_path)

def download_from_cloud_storage(bucket_name, source_blob_name, destination_file_name):
    """Downloads a file from Google Cloud Storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

def delete_from_cloud_storage(bucket_name, blob_name):
    """Deletes a file from Google Cloud Storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()

from google.cloud.exceptions import NotFound

def add_student_to_firestore(id,name,email,dob):
    """Adds a student to Firestore."""
    db = firestore.Client()
    dob = firestore.SERVER_TIMESTAMP if dob is None else dob.isoformat()

    # Check if the Firestore database exists
   
       
 
    # Now add the student
    student_ref = db.collection('students').document(str(id))
    student_ref.set({'id': id,'name': name,'email':email,'dob': dob})

    
    # Check if the collection exists, and create it if it doesn't
    
def upload_submission_to_cloud_storage(file):
    """Uploads a submission file to Google Cloud Storage."""
    # Set up Google Cloud Storage client
    storage_client = storage.Client()
    # Set the bucket name
    bucket_name = 'test_bucket_sams'
    # Set the destination file name (you can customize this as needed)
    destination_blob_name = f'submissions/{file.name}'
    # Upload the file to Cloud Storage
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(file)

def get_students_from_firestore():
    """Gets all unique students from Firestore."""
    db = firestore.Client()
    students_ref = db.collection('students').stream()
    unique_students = {}
    for student in students_ref:
        student_dict = student.to_dict()
        student_id = student_dict['id']
        # Check if the student ID is already in the set
        if student_id not in unique_students:
            unique_students[student_id] = student_dict
    # Convert the dictionary to a list of student dictionaries
    return list(unique_students.values())

def publish_message_to_pubsub(project_id, topic_id, message):
    """Publishes a message to Cloud Pub/Sub topic."""
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    data = message.encode("utf-8")
    future = publisher.publish(topic_path, data)
    future.result()

def create_bigquery_dataset(dataset_id):
    """Creates a BigQuery dataset."""
    bigquery_client = bigquery.Client()
    dataset = bigquery_client.create_dataset(dataset_id)

def load_data_to_bigquery(csv_file, dataset_id, table_id):
    """Loads data from a CSV file to a BigQuery table."""
    bigquery_client = bigquery.Client()
    dataset_ref = bigquery_client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.CSV
    job_config.skip_leading_rows = 1
    with open(csv_file, "rb") as source_file:
        job = bigquery_client.load_table_from_file(source_file, table_ref, job_config=job_config)
    job.result()

def query_bigquery(query):
    """Executes a query on BigQuery."""
    bigquery_client = bigquery.Client()
    query_job = bigquery_client.query(query)
    results = query_job.result()
    return results.to_dataframe()

def deploy_cloud_function(project_id, location, function_name, entry_point, runtime, trigger_topic):
    """Deploys a Cloud Function."""
    client = functions_v1.CloudFunctionsServiceClient()
    parent = f"projects/{project_id}/locations/{location}"
    function = {
        "name": f"projects/{project_id}/locations/{location}/functions/{function_name}",
        "entry_point": entry_point,
        "runtime": runtime,
        "event_trigger": {
            "event_type": "google.pubsub.topic.publish",
            "resource": f"projects/{project_id}/topics/{trigger_topic}",
        },
    }
    response = client.create_function(parent=parent, function=function)
    return response

def train_tensorflow_model(project_id, location, model_display_name, dataset_id, training_script_path):
    """Trains a TensorFlow model on the Cloud AI Platform."""
    aiplatform.init(project=project_id, location=location)
    dataset_path = f"projects/{project_id}/locations/{location}/datasets/{dataset_id}"
    training_job = aiplatform.CustomTrainingJob(display_name=model_display_name)
    model = training_job.run(
        base_output_dir=model_display_name,
        script_path=training_script_path,
        model_display_name=model_display_name,
        dataset=dataset_path,
    )
    return model
