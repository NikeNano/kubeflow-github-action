FROM google/cloud-sdk:alpine
# this image has all the utilities that I need and is not too bloated

LABEL "com.github.actions.name"="Submit Kubeflow Pipeline From GitHub"
LABEL "com.github.actions.icon"="upload-cloud"
LABEL "com.github.actions.color"="purple"

ENTRYPOINT ["python3 main.py"]
