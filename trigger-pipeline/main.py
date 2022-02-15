import os
import yaml
import kfp
import logging
from kfp_utils import *

def main():
    logging.info(
        "Started the process to compile and upload the pipeline to kubeflow.")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ["INPUT_GOOGLE_APPLICATION_CREDENTIALS"]
    logging.info(os.getenv("INPUT_RUN_PIPELINE"))
    logging.info(os.getenv("INPUT_EXPERIMENT_NAME"))

    logging.info("Started the process to run the pipeline on kubeflow.")
    pipeline_id = os.getenv("INPUT_PIPELINE_ID")
    run_name = os.getenv("INPUT_RUN_NAME")
    client = kfp.Client(
        host=os.getenv('INPUT_KUBEFLOW_URL'),
        client_id=os.getenv('INPUT_CLIENT_ID'),
    )

    if os.getenv("INPUT_PIPELINE_PARAMETERS_PATH") and not str.isspace(os.getenv("INPUT_PIPELINE_PARAMETERS_PATH")):
        pipeline_parameters_path = os.getenv("INPUT_PIPELINE_PARAMETERS_PATH")
    else:
        pipeline_parameters_path = None

    run_pipeline(pipeline_name=run_name,
                 pipeline_id=pipeline_id,
                 experiment_name=os.getenv("INPUT_EXPERIMENT_NAME"),
                 client=client,
                 pipeline_parameters_path=pipeline_parameters_path,
                 namespace=os.getenv("INPUT_PIPELINE_NAMESPACE"),
                 service_account=os.getenv("INPUT_PIPELINE_SERVICE_ACCOUNT"))


if __name__ == "__main__":
    main()
