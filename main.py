import os
import yaml
import kfp
import kfp.compiler as compiler
import click
import importlib.util
import logging
import sys
from datetime import datetime


logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def load_function(pipeline_function_name  :str, full_path_to_pipeline :str) -> object:
    """Function to load python function from filepath and filename
    
    Arguments:
        pipeline_function_name {str} -- The name of the pipeline function
        full_path_to_pipeline {str} -- The full path name including the filename of the python file that 
                                        describes the pipeline you want to run on Kubeflow
    
    Returns:
        object -- [description]
    """
    logging.info(f"Loading the pipeline function from: {full_path_to_pipeline}")
    logging.info(f"The name of the pipeline function is: {pipeline_function_name}")
    spec = importlib.util.spec_from_file_location(pipeline_function_name, full_path_to_pipeline)
    foo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo)
    pipeline_func = getattr(foo, pipeline_function_name)
    logging.info("Succesfully loaded the pipeline function.")
    return pipeline_func


def pipeline_compile(pipeline_function :object) -> str: 
    """Function to compile pipeline. The pipeline is compiled to a zip file. 
    
    Arguments:
        pipeline_func {object} -- The kubeflow pipeline function
    
    Returns:
        str -- The name of the compiled kubeflow pipeline
    """
    pipeline_name_zip = pipeline_function.__name__ + ".zip"
    compiler.Compiler().compile(pipeline_function, pipeline_name_zip)
    logging.info("The pipeline function is compiled.")
    return pipeline_name_zip


def upload_pipeline(pipeline_name_zip :str, pipeline_name :str, kubeflow_url :str, client_id :str) : 
    """Function to upload pipeline to kubeflow. 
    
    Arguments:
        pipeline_name_zip {str} -- The name of the compiled pipeline.ArithmeticError
        pipeline_name {str} -- The name of the pipeline function. This will be the name in the kubeflow UI. 
    """
    client = kfp.Client(
        host=kubeflow_url, 
        client_id=client_id,
        )
    client.upload_pipeline(
        pipeline_package_path=pipeline_name_zip, 
        pipeline_name=pipeline_name)
    return client

def find_pipeline_id(pipeline_name: str, client: kfp.Client, page_size: str=100, page_token: str="") -> str:
    """Function to find the pipeline id of a pipeline. 
    
    Arguments:
        pipeline_name {str} -- The name of the pipeline of interest
        client {kfp.Client} -- The kfp client
        page_size {str} -- The number of pipelines to collect a each API request
    
    Keyword Arguments:
        page_token {str} -- The page token to use for the API request (default: {" "})
    
    Returns:
        [type] -- The pipeline id. If None no match
    """
    while True: 
        pipelines = client.list_pipelines(page_size=page_size, page_token=page_token)
        for pipeline in pipelines.pipelines: 
            if pipeline.name == pipeline_name: 
                logging.info(f"The pipeline id is: {pipeline.id}")
                return pipeline.id
        # Start need to know where to do next itteration from 
        page_token = pipelines.next_page_token
        # If no next tooken break
        if not page_token:
            logging.info(f"Could not find the pipeline, is the name: {pipeline_name} correct?")
            break



def find_experiment_id(experiment_name: str, client: kfp.Client, page_size: int=100, page_token: str="") -> str:
    """Function to return the experiment id
    
    Arguments:
        experiment_name {str} -- The experiment name
        client {kfp.Client} -- The kfp client
    
    Returns:
        str -- The experiment id
    """
    while True: 
        experiments = client.list_experiments(page_size=page_size, page_token=page_token)
        for experiments in experiments.experiments: 
            if experiments.name == experiment_name: 
                logging.info("Succesfully collected the experiment id")
                return experiments.id
        # Start need to know where to do next itteration from 
        page_token = experiments.next_page_token
        # If no next tooken break
        if not page_token:
            logging.info(f"Could not find the pipeline id, is the experiment name: {experiments_name} correct? ")
            break


def read_pipeline_params(pipeline_paramters_path:str ) -> dict: 
    #[TODO] add docstring here
    pipeline_params = {}
    with open(pipeline_paramters_path) as f:
        try:
            pipeline_params = yaml.safe_load(f)
            logging.info(f"The pipeline paramters is: {pipeline_params}")
        except yaml.YAMLError as exc:
            logging.info("The yaml parameters could not be loaded correctly.")
            raise ValueError("The yaml parameters could not be loaded correctly.")
        logging.info(f"The paramters are: {pipeline_params}")
    return pipeline_params


def run_pipeline(client: kfp.Client, pipeline_name: str , pipeline_id: str, pipeline_paramters_path: dict):
    experiment_id = find_experiment_id(experiment_name=os.environ["INPUT_EXPERIMENT_NAME"], client=client)
    if not experiment_id: 
        raise ValueError("Failed to find experiment with the name: {}".format(os.environ["INPUT_EXPERIMENT_NAME"]))
    logging.info(f"The expriment id is: {experiment_id}")
    namespace = None
    if (os.getenv("INPUT_PIPELINE_NAMESPACE")!=None) and  (str.isspace(os.getenv("INPUT_PIPELINE_NAMESPACE"))==False) and os.getenv("INPUT_PIPELINE_NAMESPACE"):
        namespace = os.environ["INPUT_PIPELINE_NAMESPACE"]
        logging.info(f"The namespace that will be used is: {namespace}")
    #[TODO] What would be a good way to name the jobs
    job_name = pipeline_name + datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    logging.info(f"The job name is: {job_name}")
    
    pipeline_params = read_pipeline_params(pipeline_paramters_path=pipeline_paramters_path)
    pipeline_params = pipeline_params if pipeline_params != None else {}
    logging.info(f"experiment_id: {experiment_id}, job_name:{job_name}, pipeline_params:{pipeline_params}, pipeline_id:{pipeline_id}, namespace:{namespace}")
    client.run_pipeline(
        experiment_id=experiment_id, 
        job_name=job_name, 
        params=pipeline_params, # Read this as a yaml, people seam to prefer that to json.  
        pipeline_id=pipeline_id, 
        namespace=namespace)
    logging.info("Successfully started the pipeline, head over to kubeflow to check it out")
    

def main():
    logging.info("Started the process to compile and upload the pipeline to kubeflow.")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ["INPUT_GOOGLE_APPLICATION_CREDENTIALS"]
    pipeline_function = load_function(pipeline_function_name=os.environ['INPUT_PIPELINE_FUNCTION_NAME'], 
                                      full_path_to_pipeline=os.environ['INPUT_PIPELINE_CODE_PATH'])
    logging.info("The value of the VERSION_GITHUB_SHA is: {}".format(os.environ["INPUT_VERSION_GITHUB_SHA"]))
    if os.environ["INPUT_VERSION_GITHUB_SHA"] == "True":
        logging.info("Versioned pipeline components")
        pipeline_function = pipeline_function(github_sha=os.environ["GITHUB_SHA"])
    pipeline_name_zip = pipeline_compile(pipeline_function=pipeline_function)
    pipeline_name = os.environ['INPUT_PIPELINE_FUNCTION_NAME'] + "_" + os.environ["GITHUB_SHA"]
    client = upload_pipeline(pipeline_name_zip=pipeline_name_zip, 
                    pipeline_name=pipeline_name, 
                    kubeflow_url=os.environ['INPUT_KUBEFLOW_URL'],
                    client_id=os.environ["INPUT_CLIENT_ID"])
    if os.getenv("INPUT_RUN_PIPELINE") and os.environ["INPUT_EXPERIMENT_NAME"]:
        logging.info("Started the process to run the pipeline on kubeflow.")
        pipeline_id = find_pipeline_id(pipeline_name=pipeline_name,
            client=client)
        run_pipeline(pipeline_name=pipeline_name, 
            pipeline_id=pipeline_id, 
            client=client, 
            pipeline_paramters_path=os.environ["INPUT_PIPELINE_PARAMETERS_PATH"])


if __name__ == "__main__": 

    main()
