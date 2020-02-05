# This action Submigs Kubeflow pipelines to Kubeflow from Github Actions. 

The purpose of this action is to allow for automated deployments of [Kubeflow Pipelines](https://github.com/kubeflow/pipelines). The action will collect the pipeline from a python file and compile it before uploading it to kubeflow. The kubveflow deployment has to be using [IAP](https://www.kubeflow.org/docs/gke/deploy/monitor-iap-setup/) on GCP for this action

# Usage

## Example Workflow that uses this action 

```yaml
name: Compile and Deploy to Kubeflow
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

```

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


# Future work

Add so that pipelines can be run and scheduled to run as well. 
