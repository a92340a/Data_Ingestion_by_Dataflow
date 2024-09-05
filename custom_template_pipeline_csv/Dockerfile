FROM gcr.io/dataflow-templates-base/python310-template-launcher-base:latest

ARG DIR=/dataflow/template
RUN mkdir -p ${DIR}
WORKDIR ${DIR}
COPY requirements.txt .
COPY template_pipeline.py .

ENV FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE="${DIR}/requirements.txt"
ENV FLEX_TEMPLATE_PYTHON_PY_FILE="${DIR}/template_pipeline.py"

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r ./requirements.txt

ENTRYPOINT ["/opt/google/dataflow/python_template_launcher"]