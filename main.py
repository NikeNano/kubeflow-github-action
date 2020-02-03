import os
import kfp
import kfp.compiler as compiler
import click
import importlib.util


def load_function(pipeline_function_name  :str, full_path_to_pipeline :str) -> object:
    """Function to load python function from filepath and filename
    
    Arguments:
        pipeline_function_name {str} -- The name of the pipeline function
        full_path_to_pipeline {str} -- The full path name including the filename of the python file that 
                                        describes the pipeline you want to run on Kubeflow
    
    Returns:
        object -- [description]
    """
    spec = importlib.util.spec_from_file_location(pipeline_function_name, full_path_to_pipeline)
    foo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo)
    pipeline_func = getattr(foo, pipeline_function_name)
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

def find_pipeline_id(pipeline_name: str, client: kfp.Client, page_size: str, page_token: str=" ") -> str:
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
                return pipeline.id
        # Start need to know where to do next itteration from 
        page_token = pipelines.next_page_token
        # If no next tooken break
        if not page_token:
            break


def run_pipeline(pipeline_id: str, experiment_id: str, pipeline_paramters: dict):
    if os.getenv["INPUT_PIPELINE_NAMESPACE"]:
        namespace = os.environ["INPUT_PIPELINE_NAMESPACE"]
    client.run_pipeline(
        experiment_id=experiment_id, 
        job_name=job_name, 
        params={}, # Read this as a yaml, people seam to prefer that to json.  
        pipeline_id=pipeline_id, 
        namespace=None))
    


def main():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ["INPUT_GOOGLE_APPLICATION_CREDENTIALS"]
    pipeline_function = load_function(pipeline_function_name=os.environ['INPUT_PIPELINE_FUNCTION_NAME'], 
                                      full_path_to_pipeline=os.environ['INPUT_PIPELINE_CODE_PATH'])
    pipeline_name_zip = pipeline_compile(pipeline_function=pipeline_function)
    pipeline_name = os.environ['INPUT_PIPELINE_FUNCTION_NAME'] + "_" + os.environ["GITHUB_SHA"]
    client = upload_pipeline(pipeline_name_zip=pipeline_name_zip, 
                    pipeline_name=pipeline_name, 
                    kubeflow_url=os.environ['INPUT_KUBEFLOW_URL'],
                    client_id=os.environ["INPUT_CLIENT_ID"])

    if os.getenv("run"):
        pipeline_id = find_pipeline_id(pipeline_name=pipeline_name,
            client=client)
        experiment_id = find_experiment_id()
        run_pipeline(pipeline_id=pipeline_id, client=client)

if __name__ == "__main__": 
    main()
