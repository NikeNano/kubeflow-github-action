import click
import wget
import logging

from google.cloud import storage


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""

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

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    logging.info(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )


@click.command()
@click.option("--url", default="https://raw.githubusercontent.com/facebook/prophet/master/examples/example_wp_log_peyton_manning.csv", 
	help="the file of interest", required=False)
@click.option("--bucket", required=True, help="The name of the gcp bucket")
@click.option("--destination_blob_name", default="raw_data.csv", help="The raw data filename", required=True)
def main(url: str, bucket: str, destination_blob_name: str): 
    filename = wget.download(url)   
    upload_blob(bucket_name=bucket, source_file_name=filename, destination_blob_name=destination_blob_name)    
    logging.info("File extracted and uploaded to bucket")



if __name__ == "__main__":
    main()
