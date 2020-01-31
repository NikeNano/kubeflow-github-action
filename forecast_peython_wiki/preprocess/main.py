import click
import wget
import logging

from google.cloud import storage


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # source_blob_name = "storage-object-name"
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    logging.info(
        "Blob {} downloaded to {}.".format(
            source_blob_name, destination_file_name
        )
    )


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )


@click.command()
@click.option("--url", default="https://raw.githubusercontent.com/facebook/prophet/master/examples/example_wp_log_peyton_manning.csv", 
	help"the file of interest", required=true)
@click.option("--bucket", required=true, help="The name of the gcp bucket")
@click.option("--destination_blob_name", default="raw_data.csv", help="The raw data filename")
def main(url:str, bucket:str): 
    filename = wget.download(url)   
    upload_blob(bucket_name=bucket, source_file_name=filename, destination_blob_name=destination_blob_name)    
    logging.info("Done")



if __name__ == "__main__":
    main()
