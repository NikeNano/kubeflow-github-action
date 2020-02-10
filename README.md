# This action Submigs Kubeflow pipelines to Kubeflow from Github Actions. 

The purpose of this action is to allow for automated deployments of [Kubeflow Pipelines](https://github.com/kubeflow/pipelines). The action will collect the pipeline from a python file and compile it before uploading it to kubeflow. The kubveflow deployment has to be using [IAP](https://www.kubeflow.org/docs/gke/deploy/monitor-iap-setup/) on GCP for this action

# Usage

## Example Workflow that uses this action 


To compile a pipeline and upload it to kubeflow: 

```yaml
name: Compile and Deploy Kubeflow pipeline
on: [push]

# Set environmental variables

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - name: checkout files in repo
      uses: actions/checkout@master


    - name: Submit Kubeflow pipeline
      id: kubeflow
      uses: NikeNano/kubeflow-github-action@master
      with:
        KUBEFLOW_URL: ${{ secrets.KUBEFLOW_URL }}
        ENCODED_GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.GKE_KEY }}
        GOOGLE_APPLICATION_CREDENTIALS: /tmp/gcloud-sa.json
        CLIENT_ID: ${{ secrets.CLIENT_ID }}
        PIPELINE_CODE_PATH: "example_pipeline.py"
        PIPELINE_FUNCTION_NAME: "flipcoin_pipeline"
        PIPELINE_PARAMETERS_PATH: "parameters.yaml"
        EXPERIMENT_NAME: "Default"
        RUN_PIPELINE: False
        VERSION_GITHUB_SHA: False

```

If you also would like to run it use the following: 

```yaml
name: Compile, Deploy and Run on Kubeflow
on: [push]

# Set environmental variables

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - name: checkout files in repo
      uses: actions/checkout@master


    - name: Submit Kubeflow pipeline
      id: kubeflow
      uses: NikeNano/kubeflow-github-action@master
      with:
        KUBEFLOW_URL: ${{ secrets.KUBEFLOW_URL }}
        ENCODED_GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.GKE_KEY }}
        GOOGLE_APPLICATION_CREDENTIALS: /tmp/gcloud-sa.json
        CLIENT_ID: ${{ secrets.CLIENT_ID }}
        PIPELINE_CODE_PATH: "example_pipeline.py"
        PIPELINE_FUNCTION_NAME: "flipcoin_pipeline"
        PIPELINE_PARAMETERS_PATH: "parameters.yaml"
        EXPERIMENT_NAME: "Default"
        RUN_PIPELINE: True
        VERSION_GITHUB_SHA: False

```
The repo also contains an example where the containers in the pipeline are versioned with the github hash in order to improve operations and tracking of errors. However this requires that the pipelines function is wrapped in a function with one argument: 

```python 

  def pipeline(github_sha :str):
      ... 
      
```

and that the containers are versioned with the hash: 


```python
  pre_image = f"gcr.io/{project}/pre_image:{github_sha}"
  train_forecast_image = f"gcr.io/{project}/train_forecast_image:{github_sha}"

```
      
for example see [here](https://github.com/NikeNano/kubeflow-github-action/blob/master/forecast_peython_wiki/deployment/pipline.py)

## Mandatory inputs

1) KUBEFLOW_URL: The URL to your kubeflow deployment
2) GKE_KEY: Service account with access to kubeflow and rights to deploy, see [here](http://amygdala.github.io/kubeflow/ml/2019/08/22/remote-deploy.html) for example, the credentials needs to be bas64 encode:

``` bash
cat path-to-key.json | base64
```
3) GOOGLE_APPLICATION_CREDENTIALS: The path to where you like to store the secrets, which needs to be decoded from GKE_KEY
3) CLIENT_ID: The IAP client secret
4) PIPELINE_CODE_PATH: The full path to the python file containing the pipeline
5) PIPELINE_FUNCTION_NAME: The name of the pipeline function the PIPELINE_CODE_PATH file
6) PIPELINE_PARAMETERS_PATH: The pipeline parameters
7) EXPERIMENT_NAME: The name of the kubeflow experiment within which the pipeline should run
8) RUN_PIPELINE: If you like to also run the pipeline set "True"
9) VERSION_GITHUB_SHA: If the pipeline containers are versioned with the github hash


# Future work

Add so that pipelines can be run and scheduled to run as well. Soooon done! 
