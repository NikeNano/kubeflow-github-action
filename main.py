import os
import kfp
import kfp.compiler as compiler

def set_up(): 
    client = kfp.Client(
        host=os.environ["kubeflow_url"], 
        client_id=os.environ["client_id"]
        )
    return client

def pipeline_compile(pipeline_func:object) -> str: 
    pipeline_name_zip = pipeline_func.__name__ + ".zip"
    compiler.Compiler().compile(pipeline_func, pipeline_name_zip)
    return pipeline_name_zip


def upload_pipeline(pipeline_name_zip:str,, pipeline_name:str)
    client = kfp.Client(
        host=os.environ["kubeflow_url"], 
        client_id=os.environ["client_id"]
        )
    client.upload_pipeline(
        pipeline_package_path=pipeline_filename, 
        pipeline_name=pipeline_name)

def load_function():
    import importlib.util
    spec = importlib.util.spec_from_file_location("test_func", "test.py")
    foo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo)

def main():



if __name__ == "__main__": 
    main()
