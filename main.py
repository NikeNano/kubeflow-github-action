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
        client_id=client_id
        )
    client.upload_pipeline(
        pipeline_package_path=pipeline_name_zip, 
        pipeline_name=pipeline_name)
    return client

@click.command()
@click.option('-p', '--pipeline_function_name', required=True, type=str)
@click.option('-c', '--pipeline_code_path', required=True, type=str)
@click.option('-u','--kubeflow_url', required=True, type=str)
@click.option('-i','--client_id', required=True, type=str)
def main(pipeline_function_name:str, pipeline_code_path:str , kubeflow_url:str, client_id:str):
    pipeline_function = load_function(pipeline_function_name=pipeline_function_name, 
                                      full_path_to_pipeline=pipeline_code_path)
    pipeline_name_zip = pipeline_compile(pipeline_function=pipeline_function)
    client = upload_pipeline(pipeline_name_zip=pipeline_name_zip, 
                    pipeline_name=pipeline_function_name, 
                    kubeflow_url=kubeflow_url,
                    client_id=client_id)


if __name__ == "__main__": 
    main()
