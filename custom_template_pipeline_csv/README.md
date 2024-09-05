# Data ingestion by dataflow - A complete use case (CSV)
Using Apache Beam to custom Dataflow ingestion service.

## Scenario
Beam pipeline built with custom flex template and running on Dataflow Runner to ingest, process and store data. 
By using a specific Dataflow base image (e.g., `python310-template-launcher-base`) along with required files like `requirements.txt` and `template_pipeline.py`, you can build a consistent, portable container image. This approach ensures clear version control, simplifies deployment across different environments, making collaboration with multiple team members more efficient.

## Architecture
Run a custom Apache Beam data pipeline with Dataflow custom flex template  
![architecture_complete_use_case](/images/architecture_complete_use_case.jpg)

#### Cloud Storage
Store Dataflow staging files and template files
- BUCKET NAME: `solution-data-ingestion-by-dataflow`

#### Dataflow
Data pipeline jobs with parameters(pipeline options) and job information
- JOB NAME: custom-pipeline-to-bigquery-`<%Y%m%d-%H%M%S>`

#### BigQuery
Destination table in BigQuery
- DATASET NAME: `solution_data_ingestion_by_dataflow`

#### Artifact Registry
Publish the Docker container image for the template.
- REPOSITORY NAME: `solution-data-ingestion-by-dataflow`


## How to use
### 1. Set environment variables
Pre-requirement for following command usage:
```shell
export PROJECT_ID=tw-rd-de-data-solution
export DATAFLOW_REGION=asia-east1
export BUCKET_NAME=solution-data-ingestion-by-dataflow
export DATASET_NAME=solution_data_ingestion_by_dataflow
export DATAFLOW_REPOSITORY=solution-data-ingestion-by-dataflow  
export IMAGE_NAME=custom_template_to_bigquery
export IMAGE_VERSION=1.0
```

### 2. prepare input files 
This custom flex template only supports input format: CSV. 
List of mock data: 
- CSV: `gs://na_data_internal/sample_file/sample_data.csv`


### 3. Build container images
Building container images with a specific Dataflow base image (e.g., `python310-template-launcher-base`) and required files like `requirements.txt` and `template_pipeline.py`. 
```shell
docker build -t $DATAFLOW_REGION-docker.pkg.dev/$PROJECT_ID/$DATAFLOW_REPOSITORY/$IMAGE_NAME:$IMAGE_VERSION .

gcloud auth configure-docker $DATAFLOW_REGION-docker.pkg.dev

docker push $DATAFLOW_REGION-docker.pkg.dev/$PROJECT_ID/$DATAFLOW_REPOSITORY/$IMAGE_NAME:$IMAGE_VERSION
```

### 4. Build dataflow templates
This step creates a custom flex template using the metadata.json combining with container image, and uploads the template file (e.g., `custom_template_to_bigquery.json`) to the specified GCS location as the output.
```shell
gcloud dataflow flex-template build gs://$BUCKET_NAME/template/custom_template_to_bigquery.json \
    --image "$DATAFLOW_REGION-docker.pkg.dev/$PROJECT_ID/$DATAFLOW_REPOSITORY/$IMAGE_NAME:$IMAGE_VERSION" \
    --sdk-language "PYTHON" \
    --metadata-file metadata.json \
    --project $PROJECT_ID
```

### 5. Using command line to execute data pipeline with custom flex template
Parameters desctiption:
- project: Your project id (set by 'PROJECT_ID')
- region: The region your pipeline service built in (set by 'DATAFLOW_REGION')
- repository: Artifact Registry with custom template image (set by 'DATAFLOW_REPOSITORY')
- inputFilePath: Your source file path starting with `gs://` 
- outputTable: BigQuery table name compiled with 'dataset.table' or 'project:dataset.table' pattern
- schemaJSONPath (optional): BigQuery table schema file path starting with `gs://` 
- chunkSize (optional): Number of lines to read from the file per chunk
- csvFileEncoding (optional): The CSV file character encoding format
- isTrucate (optional): Whether the table is needed to truncate

```shell
gcloud dataflow flex-template run "custom-pipeline-to-bigquery-`date +%Y%m%d-%H%M%S`" \
    --template-file-gcs-location "gs://$BUCKET_NAME/template/custom_template_to_bigquery.json" \
    --project $PROJECT_ID \
    --region $DATAFLOW_REGION \
    --parameters inputFilePath=gs://na_data_internal/sample_file/sample_data.csv \
    --parameters outputTable=$PROJECT_ID:$DATASET_NAME.csv_output \
    --parameters schemaJSONPath=gs://solution-data-ingestion-by-dataflow/template/schema.json \
    --parameters isTruncate=true
```

