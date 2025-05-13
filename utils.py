import os
from azure.storage.blob import BlobServiceClient, ContentSettings
from dotenv import load_dotenv
load_dotenv()

connection_string = os.getenv("AZURE_CONNECTION_STRING")
container_name = os.getenv("AZURE_CONTAINER_NAME")

# Initialize BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Get the container client
container_client = blob_service_client.get_container_client(container_name)

# Function to download a file from Azure Blob Storage
def download_blob_from_storage(blob_name, download_path):
    try:
        # Get the BlobClient
        blob_client = container_client.get_blob_client(blob_name)

        # Download the blob to a local file
        with open(download_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

        print(f"Downloaded '{blob_name}' to '{download_path}'.")

    except Exception as e:
        print(f"Error downloading file: {e}")

# Function to list and download all files in a folder
def download_all_files_in_folder(model_folder,local_model_folder):
    try:
        # List all blobs in the container
        blobs = container_client.list_blobs(name_starts_with=model_folder)

        for blob in blobs:
            blob_name = blob.name
            # Create the local directory structure if it doesn't exist
            local_file_path = os.path.join(local_model_folder, os.path.relpath(blob_name, model_folder))
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

            # Download each blob
            download_blob_from_storage(blob_name, local_file_path)

    except Exception as e:
        print(f"Error downloading files: {e}")

