import os
import kfp
import kfp.compiler as compiler
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


def pipeline_compile(pipeline_function_name :object) -> str: 
    """Function to compile pipeline. The pipeline is compiled to a zip file. 
    
    Arguments:
        pipeline_func {object} -- The kubeflow pipeline function
    
    Returns:
        str -- The name of the compiled kubeflow pipeline
    """
    pipeline_name_zip = pipeline_func.__name__ + ".zip"
    compiler.Compiler().compile(pipeline_func, pipeline_name_zip)
    return pipeline_name_zip


def upload_pipeline(pipeline_name_zip :str, pipeline_name :str): 
    """Function to upload pipeline to kubeflow. 
    
    Arguments:
        pipeline_name_zip {str} -- The name of the compiled pipeline.ArithmeticError
        pipeline_name {str} -- The name of the pipeline function. This will be the name in the kubeflow UI. 
    """
    client = kfp.Client(
        host=os.environ["kubeflow_url"], 
        client_id=os.environ["client_id"]
        )
    client.upload_pipeline(
        pipeline_package_path=pipeline_filename, 
        pipeline_name=pipeline_name)
    return client


def main():
    pipeline_function = load_function(pipeline_function_name=os.environ["pipeline_function_name"]
                                      full_path_to_pipeline=os.environ["pipeline_code_path"])
    pipeline_name_zip = pipeline_compile(pipeline_function_name=pipeline_function)
    client = upload_pipeline(pipeline_name_zip=pipeline_name_zip, 
                    pipeline_name=os.environ["pipeline_function_name"])


if __name__ == "__main__": 
    main()
