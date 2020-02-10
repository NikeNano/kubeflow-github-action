import kfp
import datetime
import os
import click
import logging

@kfp.dsl.pipeline(
    name="Example pipeline github action"
    description="This pipeline show how you can version the pipeline components using the githash"
)
def timeseries_pipeline(gcp_bucket: str, project: str, github_sha: str, train_data :str="train.csv", forecast_date: str="forecast.csv"): 
    pre_image = f"gcr.io/{project}/pre_image:{github_sha}"
    train_forecast_image = f"gcr.io/{project}/train_forecast_image:{github_sha}"

    operations['preprocess'] = dsl.ContainerOp(
        name='Preprocess',
        image=pre_image,
        command=['python3'],
        arguments=["main.py",
                  "--url", "https://raw.githubusercontent.com/facebook/prophet/master/examples/example_wp_log_peyton_manning.csv",
                  "--bucket", gcp_bucket
                  "--destination_blob_name", train_data
        ]
      ).apply(use_secret(secret_name=secret_database_name, volume_name="mysecretvolume-one", secret_volume_mount_path=secret_volume_mount_path_sandtrade_database)) \
          .set_image_pull_policy('Always')

    operations['train_forecast'] = dsl.ContainerOp(
        name='Forecast',
        image=pre_image,
        command=['python3'],
        arguments=["main.py",
                  "--bucket", gcp_bucket
                  "--source_blob_name", train_data
                  "--forecast_blob_name", forecast_date
        ]
      ).apply(use_secret(secret_name=secret_database_name, volume_name="mysecretvolume-one", secret_volume_mount_path=secret_volume_mount_path_sandtrade_database)) \
          .set_image_pull_policy('Always')