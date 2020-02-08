import click
import wget
import logging

from google.cloud import storage


def upload_blob(bucket_name: str, source_file_name: str, destination_blob_name: str):
    """Function to upload to gcp bucket
    
    Arguments:
        bucket_name {str} -- The name of the bucket.
        source_file_name {str} -- The name of the source file that should be uploaded.
        destination_blob_name {str} -- The name of the file in the bucket. 
    """
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
