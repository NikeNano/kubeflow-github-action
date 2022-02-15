FROM python:3.7-stretch

LABEL "com.github.actions.name"="Submit Kubeflow Pipeline From GitHub"
LABEL "com.github.actions.icon"="upload-cloud"
LABEL "com.github.actions.color"="purple"

COPY . . 

RUN chmod +x /entrypoint.sh

RUN pip install -r requirements.txt
RUN pip install kfp --upgrade

ENTRYPOINT ["/entrypoint.sh"]
