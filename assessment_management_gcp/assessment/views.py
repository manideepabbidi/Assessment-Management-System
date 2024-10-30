# assessment/views.py

from django.shortcuts import render, redirect
from .models import Student, Course, Enrollment, Assignment, Submission
from . import gcp_utils
from google.cloud import storage, firestore, pubsub_v1
from google.cloud import bigquery
from django.http import HttpResponse
import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from firebase_admin import firestore
from google.cloud import storage, pubsub_v1
import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from firebase_admin import firestore
from google.cloud import storage, pubsub_v1
import tensorflow as tf

# Initialize Firestore, Cloud Storage, and Pub/Sub clients
db = firestore.client()
storage_client = storage.Client()
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path('sams-420304', 'test')  # Replace with your GCP project ID and Pub/Sub topic name


from django.shortcuts import render, redirect
from .models import Student, Course, Assignment, Submission
from .forms import StudentForm, CourseForm, AssignmentForm, SubmissionForm

def home(request):
    # Add logic for dashboard view
    return render(request, 'home.html')


def create_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # Assuming 'student_list' is the URL name for listing students
    else:
        form = StudentForm()
    return render(request, 'create_student.html', {'form': form})

def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return  redirect('home')   # Assuming 'course_list' is the URL name for listing courses
    else:
        form = CourseForm()
    return render(request, 'create_course.html', {'form': form})

def create_assignment(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
           
            form.save()
            return  redirect('home') # Assuming 'assignment_list' is the URL name for listing assignments
    else:
        form = AssignmentForm()
        form.fields['course'].queryset = Course.objects.all()
    return render(request, 'create_assignment.html', {'form': form})

def submit_assignment(request):
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to assignment list after submission
    else:
        form = SubmissionForm()
    return render(request, 'submit_assignment.html', {'form': form})
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Student, Course, Enrollment, Assignment, Submission
from google.cloud import firestore

# Initialize Firestore client
db = firestore.Client()

# Function to store an object in Firestore
def store_in_firestore(collection_name, data):
    doc_ref = db.collection(collection_name).document()
    doc_ref.set(data)

# Define receiver functions for each model
@receiver(post_save, sender=Student)
def student_post_save(sender, instance, created, **kwargs):
    if created:
        data = {
            'id': instance.id,
            'name': instance.name,
            'email': instance.email,
            'dob': instance.date_of_birth.strftime('%Y-%m-%d')
            # Add more fields as needed
        }
        
        store_in_firestore('students', data)

@receiver(post_save, sender=Course)
def course_post_save(sender, instance, created, **kwargs):
    if created:
        data = {
            'name': instance.name,
            'description': instance.description,
            # Add more fields as needed
        }
        store_in_firestore('courses', data)

@receiver(post_save, sender=Assignment)
def assignment_post_save(sender, instance, created, **kwargs):
    if created:
        data = {
            'name': instance.name,
            'description': instance.description,
            'due_date': instance.due_date.strftime('%Y-%m-%d'),
            'course': instance.course.name
                      # Add more fields as needed
        }
        store_in_firestore('assignments', data)

# Implement similar receiver functions for Enrollment and Submission models if needed
@receiver(post_save, sender='assessment.Enrollment')
def process_enrollment(sender, instance, **kwargs):
    """Triggered by a change to any Enrollment instance."""
    bucket_name = 'test_bucket_sams'  # Replace with your GCP bucket name
    if instance:
        data = {
            'student_id': instance.student.id,
            'course': instance.course.name,
            'enrollment_date': instance.enrollment_date.strftime('%Y-%m-%d'),
            # Add more fields as needed
        }
        file_name = f"enrollments/{instance.id}.json"  # File name format: enrollments/<enrollment_id>.json
        upload_to_bucket(bucket_name, file_name, json.dumps(data))
        publish_to_pubsub(json.dumps(data))

# Receiver function for Submission model
@receiver(post_save, sender='assessment.Submission')
def process_submission(sender, instance, **kwargs):
    """Triggered by a change to any Submission instance."""
    bucket_name = 'test_bucket_sams'  # Replace with your GCP bucket name
    if instance:
        data = {
            'student_id': instance.student.id,
            'assignment_id': instance.assignment.id,
            'submission_date': instance.submission_date.strftime('%Y-%m-%d'),
            # Add more fields as needed
        }
        file_name = f"submissions/{instance.id}.json"  # File name format: submissions/<submission_id>.json
        #print("Success")
        upload_to_bucket(bucket_name, file_name, json.dumps(data))
        print("Success")
        publish_to_pubsub(json.dumps(data))

# Helper functions
def upload_to_bucket(bucket_name, file_name, data):
    """Uploads data to a GCP bucket."""
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_string(data)

def publish_to_pubsub(data):
    """Publishes message to a Pub/Sub topic."""
    data = data.encode('utf-8')
    future = publisher.publish(topic_path, data)
    future.result()





from google.cloud import firestore, storage, bigquery
from assessment.bigquery import *
from google.cloud import bigquery
#from looker_sdk import client, models
from google.auth import compute_engine
from google.auth.transport.requests import Request

def analyze_and_export_to_bigquery(request):
    project_id = "sams-420304"
    dataset_id = "test_db"
    bucket_name = "test_bucket_sams"
    folder_path = "submissions"

    # Fetch data from Firestore students collection
    student_data = fetch_students_data()

    # Fetch data from the GCS bucket
    submission_data = fetch_submissions_data(bucket_name, folder_path)

    # Insert student data into BigQuery
    students_schema = [
    bigquery.SchemaField("id", "STRING"),
    bigquery.SchemaField("name", "STRING"),
    bigquery.SchemaField("dob", "DATE"),
    bigquery.SchemaField("email", "STRING"),
    # Add more fields as needed
]
    #create_table_if_not_exists(dataset_id, "students", students_schema)
    insert_students_data(project_id, dataset_id, "students", student_data)

    # Insert submission data into BigQuery
    submissions_schema = [
        bigquery.SchemaField("student_id", "STRING"),
        bigquery.SchemaField("assignment_id", "INTEGER"),
        bigquery.SchemaField("submission_date", "DATE"),
        # Add more fields as needed
    ]
    #create_table_if_not_exists(dataset_id, "submissions", submissions_schema)
    insert_submissions_data(project_id, dataset_id, "submissions", submission_data)
    #sdk = client.init31()
   
    #model = models.WriteModel(name="StudentSubmissions", project_name="SAMS", explores=[models.WriteModelExplore(name="student_submissions")])
    #sdk.create_lookml_model("SAMS", model)
    visualization_url = construct_visualization_url(project_id, dataset_id)

    # Redirect the user to the visualization URL
    return redirect(visualization_url)


    return render(request, 'analyze.html', {'visualization_url'})
# assessment/views.py
def construct_visualization_url(project_id, dataset_id):
    # Construct the visualization URL based on your requirements
    # Example URL format for BigQuery's Data Studio integration:
    # https://datastudio.google.com/reporting/<report_id>/page/<page_id>?params=<dataset_id>
    visualization_url = f"https://lookerstudio.google.com/reporting/666be5ff-51c2-487f-b707-9aaf5b40133d/page/xEpwD?params={dataset_id}"
    return visualization_url
import tensorflow as tf
import json
from django.http import JsonResponse
from google.cloud import storage

def preprocess_data(data):
    """
    Preprocesses the data before analysis.

    Args:
    - data: The data dictionary containing student ID, assignment ID, and submission date.

    Returns:
    - preprocessed_data: Preprocessed data ready for analysis.
    """
    # Convert student ID to integer
    student_id = int(data['student_id'])

    # Convert assignment ID to integer
    assignment_id = int(data['assignment_id'])

    # Parse submission date as a datetime object
    submission_date = data['submission_date']

    # Perform any additional preprocessing if needed

    # Create a preprocessed data dictionary
    preprocessed_data = {
        'student_id': student_id,
        'assignment_id': assignment_id,
        'submission_date': submission_date
    }

    return preprocessed_data

def analyze_data(data):
    """
    Analyzes the preprocessed data to provide insights.

    Args:
    - data: The preprocessed data dictionary.

    Returns:
    - insights: Insights derived from the data.
    """
    # Perform analysis based on the data
    # For example, you can calculate statistics, identify patterns, etc.

    # Further analyze the predictions or incorporate them into insights
    # For example, calculate statistics or identify patterns in the predictions

    # Generate insights based on the predictions or other analysis
    insights = {
        'message': 'Data analysis performed successfully!',
        'predictions': data# Convert predictions to list for JSON serialization
        # You can include additional insights here based on the analysis
    }

    return insights

def train_model(request):
    if request.method == 'GET':
        try:
            # Initialize a GCS client
            storage_client = storage.Client()

            # Specify your GCS bucket name and file path
            bucket_name = 'test_bucket_sams'
            folder_path = 'submissions/'

            # Retrieve all the files within the specified folder in the GCS bucket
            bucket = storage_client.get_bucket(bucket_name)
            blobs = bucket.list_blobs(prefix=folder_path)

            # Initialize an empty list to store data from each file
            all_data = []

            # Iterate over the files in the folder
            for blob in blobs:
                # Download the file and process its content
                data = blob.download_as_string()

                # Assuming the data in each file is in JSON format
                # You may need to adjust this parsing logic if the data is in a different format
                data_dict = json.loads(data)

                # Append the processed data to the list
                all_data.append(data_dict)

            # Retrieve the file from the GCS bucket
            '''bucket = storage_client.get_bucket(bucket_name)
            blob = bucket.blob(file_path)
            data = json.loads(blob.download_as_string())'''
            #print(all_data)
            # Preprocess the data
            preprocessed_data_list = []

# Iterate through each data dictionary in the list
            for data_dict in all_data:
    # Preprocess each data dictionary
                preprocessed_data = preprocess_data(data_dict)
                preprocessed_data_list.append(preprocessed_data)
            #print("Process")
            #print(preprocess_data)
            # Analyze the preprocessed data
            insights = analyze_data(preprocessed_data_list)

            # Return insights as JSON response
            return JsonResponse(insights)

        except Exception as e:
            # Return an error response if any exception occurs
            return JsonResponse({'error': str(e)}, status=500)

    else:
        # Return an error response if the request method is not GET
        return JsonResponse({'error': 'GET method required!'}, status=405)

'''
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def prepare_data(data):
    """
    Preprocesses the data and prepares it for training.

    Args:
    - data: The data dictionary retrieved from Firestore.

    Returns:
    - X_train: Preprocessed features for training.
    - X_test: Preprocessed features for testing.
    - y_train: Target labels for training.
    - y_test: Target labels for testing.
    """
    # Extract features and target labels from the data
    features = data['features']
    labels = data['labels']

    # Preprocess the features (e.g., scale them)
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(features_scaled, labels, test_size=0.2, random_state=42)

    return X_train, X_test, y_train, y_test

def train_tensorflow_model(data):
    """
    Trains a TensorFlow model using the provided data.

    Args:
    - data: The data dictionary retrieved from Firestore.

    Returns:
    - model: The trained TensorFlow model.
    """
    # Prepare the data for training
    X_train, X_test, y_train, y_test = prepare_data(data)

    # Define the TensorFlow model architecture
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])

    # Compile the model
    model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    # Train the model
    model.fit(X_train, y_train, epochs=10, validation_data=(X_test, y_test))

    return model
from django.http import JsonResponse

import json
from django.http import JsonResponse
from google.cloud import storage

def train_model(request):
    if request.method == 'GET':
        # Initialize a GCS client
        storage_client = storage.Client()

        # Specify your GCS bucket name and folder path
        bucket_name = 'test_bucket_sams'
        folder_path = 'submissions/'

        try:
            # Retrieve all the files within the specified folder in the GCS bucket
            bucket = storage_client.get_bucket(bucket_name)
            blobs = bucket.list_blobs(prefix=folder_path)

            # Initialize an empty list to store data from each file
            all_data = []

            # Iterate over the files in the folder
            for blob in blobs:
                # Download the file and process its content
                data = blob.download_as_string()

                # Assuming the data in each file is in JSON format
                # You may need to adjust this parsing logic if the data is in a different format
                data_dict = json.loads(data)

                # Append the processed data to the list
                all_data.append(data_dict)

            # Train the TensorFlow model with all the retrieved data
            trained_model = train_tensorflow_model(all_data)

            # Return a JSON response indicating success
            return JsonResponse({'message': 'Model trained successfully!'})
        
        except Exception as e:
            # Return an error response if any exception occurs
            return JsonResponse({'error': str(e)}, status=500)
    
    else:
        # Return an error response if the request method is not GET
        return JsonResponse({'error': 'GET method required!'}, status=405) 
'''
