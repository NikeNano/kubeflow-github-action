import os
import yaml
import kfp
import logging
from kfp_utils import *

def main():
    logging.info(
        "Started the process to compile and upload the pipeline to kubeflow.")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ["INPUT_GOOGLE_APPLICATION_CREDENTIALS"]
    pipeline_function = load_function(pipeline_function_name=os.getenv('INPUT_PIPELINE_FUNCTION_NAME'),
                                      full_path_to_pipeline=os.getenv('INPUT_PIPELINE_CODE_PATH'))
    logging.info("The value of the VERSION_GITHUB_SHA is: {}".format(
        os.getenv("INPUT_VERSION_GITHUB_SHA")))
    if os.getenv("INPUT_VERSION_GITHUB_SHA") and os.getenv("INPUT_VERSION_GITHUB_SHA").lower() == "true":
        logging.info("Versioned pipeline components")
        pipeline_function = pipeline_function(github_sha=os.getenv("GITHUB_SHA"))

    v2_compatible = os.getenv("INPUT_V2_COMPATIBLE") and os.getenv("INPUT_V2_COMPATIBLE").lower() == "true"
    pipeline_name_zip = pipeline_compile(pipeline_function=pipeline_function, v2_compatible=v2_compatible)
    pipeline_name = os.getenv('INPUT_PIPELINE_FUNCTION_NAME') + \
        "_" + os.getenv("GITHUB_SHA")
    client = upload_pipeline(pipeline_name_zip=pipeline_name_zip,
                             pipeline_name=pipeline_name,
                             kubeflow_url=os.getenv('INPUT_KUBEFLOW_URL'),
                             client_id=os.getenv("INPUT_CLIENT_ID"))
    logging.info(os.getenv("INPUT_RUN_PIPELINE"))
    logging.info(os.getenv("INPUT_EXPERIMENT_NAME"))
    if os.getenv("INPUT_RUN_PIPELINE") and os.getenv("INPUT_RUN_PIPELINE").lower() == "true":
        logging.info("Started the process to run the pipeline on kubeflow.")
        pipeline_id = find_pipeline_id(pipeline_name=pipeline_name,
                                       client=client)

        if os.getenv("INPUT_PIPELINE_PARAMETERS_PATH") and not str.isspace(os.getenv("INPUT_PIPELINE_PARAMETERS_PATH")):
            pipeline_parameters_path = os.getenv("INPUT_PIPELINE_PARAMETERS_PATH")
        else:
            pipeline_parameters_path = None

        run_pipeline(pipeline_name=pipeline_name,
                     pipeline_id=pipeline_id,
                     experiment_name=os.getenv("INPUT_EXPERIMENT_NAME"),
                     client=client,
                     pipeline_parameters_path=pipeline_parameters_path,
                     namespace=os.getenv("INPUT_PIPELINE_NAMESPACE"),
                     service_account=os.getenv("INPUT_PIPELINE_SERVICE_ACCOUNT"))


if __name__ == "__main__":
    main()
