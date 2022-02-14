import os
import yaml
import kfp
import logging
from kfp_utils import *

def main():
    logging.info(
        "Started the process to compile and upload the pipeline to kubeflow.")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ["INPUT_GOOGLE_APPLICATION_CREDENTIALS"]
    pipeline_function = load_function(pipeline_function_name=os.environ['INPUT_PIPELINE_FUNCTION_NAME'],
                                      full_path_to_pipeline=os.environ['INPUT_PIPELINE_CODE_PATH'])
    logging.info("The value of the VERSION_GITHUB_SHA is: {}".format(
        os.environ["INPUT_VERSION_GITHUB_SHA"]))
    if os.environ["INPUT_VERSION_GITHUB_SHA"] == "true":
        logging.info("Versioned pipeline components")
        pipeline_function = pipeline_function(
            github_sha=os.environ["GITHUB_SHA"])
    pipeline_name_zip = pipeline_compile(pipeline_function=pipeline_function)
    pipeline_name = os.environ['INPUT_PIPELINE_FUNCTION_NAME'] + \
        "_" + os.environ["GITHUB_SHA"]
    client = upload_pipeline(pipeline_name_zip=pipeline_name_zip,
                             pipeline_name=pipeline_name,
                             kubeflow_url=os.environ['INPUT_KUBEFLOW_URL'],
                             client_id=os.environ["INPUT_CLIENT_ID"])
    logging.info(os.getenv("INPUT_RUN_PIPELINE"))
    logging.info(os.environ["INPUT_EXPERIMENT_NAME"])
    if os.getenv("INPUT_RUN_PIPELINE") == "true" and os.environ["INPUT_EXPERIMENT_NAME"]:
        logging.info("Started the process to run the pipeline on kubeflow.")
        pipeline_id = find_pipeline_id(pipeline_name=pipeline_name,
                                       client=client)

        if os.getenv("INPUT_PIPELINE_PARAMETERS_PATH") and not str.isspace(os.getenv("INPUT_PIPELINE_PARAMETERS_PATH")):
            pipeline_parameters_path = os.getenv("INPUT_PIPELINE_PARAMETERS_PATH")
        else:
            pipeline_parameters_path = None

        run_pipeline(pipeline_name=pipeline_name,
                     pipeline_id=pipeline_id,
                     client=client,
                     pipeline_parameters_path=pipeline_parameters_path,
                     namespace=os.environ["INPUT_PIPELINE_NAMESPACE"])


if __name__ == "__main__":
    main()
