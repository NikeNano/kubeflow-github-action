import kfp
import datetime
import os
import click
import logging

@kfp.dsl.pipeline(
    name="Example pipeline github action"
    description="This pipeline show how you can version the pipeline components using the githash"
)
def timeseries_pipeline(gcp_bucket: str, project: str, github_sha: str): 

    pre_image = f"gcr.io/{project}/pre_image:{github_sha}"
    train_forecast_image = f"gcr.io/{project}/train_forecast_image:{github_sha}"