import pandas as pd
import tempfile
import click
import logging
import os 

from fbprophet import Prophet
from google.cloud import storage

def download_blob(bucket_name: str, source_blob_name: str, destination_file_name: str):
    """Function to download file from gcp bucet
    
    Arguments:
        bucket_name {str} -- The name of the bucket from which the data should be downloaded.
        source_blob_name {str} -- The name of the file in the bucket which should be downloaded.
        destination_file_name {str} -- The local file pat for the downloaded file. 
    """

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    logging.info(
        "Blob {} downloaded to {}.".format(
            source_blob_name, destination_file_name
        )
    )


def upload_blob(bucket_name: str, source_file_name: str, destination_blob_name: str):
    """Function to upload file to bucket. 
    
    Arguments:
        bucket_name {str} -- The name of the bucket on gcp.
        source_file_name {str} -- The filepath to the file that should be uploaded.
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
@click.option("--bucket", required=True, help="The name of the gcp bucket")
@click.option("--source_blob_name", default="raw_data.csv", help="The raw file to download", required=True)
@click.option("--forecast_blob_name", default="raw_data.csv", help="The forecast to upload", required=True)
def main(bucket: str, source_blob_name :str, forecast_blob_name:str):
    with tempfile.TemporaryDirectory() as tmpdirname:
        local_file = os.path.join(tmpdirname,"tmp.csv") 
        download_blob(bucket_name=bucket, source_blob_name=source_blob_name, destination_file_name=local_file)
        df = pd.read_csv(local_file)
    # Train the model
    m = Prophet()
    logging.info("Starting training of the prophet model")
    m.fit(df)
    logging.info("The Propeht model is trained")
    future = m.make_future_dataframe(periods=365)
    forecast = m.predict(future)
    with tempfile.TemporaryDirectory() as tmpdirname:
        forecast_file = os.path.join(tmpdirname, "forecast.csv")
        forecast.to_csv(forecast_file)
        upload_blob(bucket_name=bucket, source_file_name=forecast_file, destination_blob_name=forecast_blob_name)
    logging.info("The model training is done and forecasting is done")


if __name__ == "__main__":
    main()
