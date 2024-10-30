# assessment/signals.py

import os
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
topic_path = publisher.topic_path('sams-420304', 'test-topic')  # Replace with your GCP project ID and Pub/Sub topic name


@receiver(post_save)
def process_document(sender, instance, **kwargs):
    """Triggered by a change to any Firestore document."""
    if sender._meta.app_label == 'assessment':
        bucket_name = os.environ.get('GCP_BUCKET_NAME')
        if not bucket_name:
            raise ValueError("GCP_BUCKET_NAME environment variable not set")

        # Get the Firestore document data
        doc_ref = db.collection('your_collection_name').document()  # Adjust 'your_collection_name' to the Firestore collection name
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            file_name = f"{instance._meta.model_name}.json"  # File name format: <model_name>/<document_id>.json
            upload_to_bucket(bucket_name, file_name, json.dumps(data))
            publish_to_pubsub(json.dumps(data))
            train_tensorflow_model(data)  # Call TensorFlow model training function

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

