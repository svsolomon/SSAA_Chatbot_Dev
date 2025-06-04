import os
from azure.storage.blob import BlobServiceClient, ContentSettings
from dotenv import load_dotenv
load_dotenv()

# Load environment variables
connection_string = os.getenv("AZURE_CONNECTION_STRING")
container_name = os.getenv("AZURE_CONTAINER_NAME")

# Initialize BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Get the container client
container_client = blob_service_client.get_container_client(container_name)

def download_blob_from_storage(blob_name: str, download_path: str) -> None:
    """
    Downloads a single blob (file) from Azure Blob Storage to a specified local path.

    Parameters:
    -----------
    blob_name (str): The name/path of the blob in the container.
    download_path (str): The full local file path where the blob will be saved.

    Returns:
    --------
    None
    """
    try:
        # Get a reference to the blob
        blob_client = container_client.get_blob_client(blob_name)

        # Write the blob content to a local file
        with open(download_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

        print(f"Downloaded '{blob_name}' to '{download_path}'.")

    except Exception as e:
        print(f"Error downloading file: {e}")

def download_all_files_in_folder(model_folder: str, local_model_folder: str) -> None:
    """
    Downloads all blobs from a specified folder in Azure Blob Storage to a local directory.

    Parameters:
    -----------
    model_folder (str): The folder name (prefix) in the container where model files are stored.
    local_model_folder (str): The local directory where downloaded files will be saved.

    Returns:
    --------
    None
    """
    try:
        # List all blobs that start with the given folder name
        blobs = container_client.list_blobs(name_starts_with=model_folder)

        for blob in blobs:
            blob_name = blob.name

            # Construct the full local path preserving subdirectory structure
            local_file_path = os.path.join(local_model_folder, os.path.relpath(blob_name, model_folder))
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

            # Download the blob
            download_blob_from_storage(blob_name, local_file_path)

    except Exception as e:
        print(f"Error downloading files: {e}")
