# Data ingestion by dataflow - A Simple Use Case
Using Apache Beam to custom Dataflow ingestion service.

## Scenario
Beam pipeline with Dataflow Runner to ingest, process and store data. Without building images on Artifact Registry and declaring parameters in metadata, it's a more common way in development stage to satisfy the various situations and uncertain demands. 

## Architecture
### 1. A Simple Use Case
Run a custom Apache Beam data pipeline on Dataflow without template  
![architecture_simple_use_case](/images/architecture_simple_use_case.jpg)

#### Cloud Storage
Store Dataflow staging files and template files
- BUCKET NAME: `solution-data-ingestion-by-dataflow`

#### Dataflow
Data pipeline jobs with parameters(pipeline options) and job information
- JOB NAME (default): beamapp-`<username>`-uuid()

#### BigQuery
Destination table in BigQuery
- DATASET NAME: `solution_data_ingestion_by_dataflow`
- TABLE NAME: `csv_ouput`, `json_output`, `parquet_output`


## How to use
### 1. Set environment variables
```shell
export PROJECT_ID=tw-rd-de-data-solution
export DATAFLOW_REGION=asia-east1
export BUCKET_NAME=solution-data-ingestion-by-dataflow
export DATASET_NAME=solution_data_ingestion_by_dataflow
```

### 2. prepare input files 
There are 3 types of supported input format: CSV, JSON(Newline), Parquet. 
List of mock data: 
- CSV: `gs://na_data_internal/sample_file/sample_data.csv`
- JSON (Newline): `gs://na_data_internal/sample_file/sample_data.txt` 
- Parquet: `gs://na_data_internal/sample_file/sample_data.parquet`


### 3. Using command line to execute data pipeline
Parameters description:
- project: Your project id (set by 'PROJECT_ID')
- region: The region your pipeline service built in (set by 'DATAFLOW_REGION')
- input: Your source file path
- output: BigQuery table name compiled with 'dataset.table' or 'project:dataset.table' pattern
- schema (optional): BigQuery table schema compiled with 'column1:datatype1,column2:datatyp2e' pattern
- runner: 'DirectRunner' (default), 'DataflowRunner' and other distributed system (more info: https://beam.apache.org/get-started/wordcount-example/#direct-runner)
- temp_location: Your data staging location as processing transformation

Example deployment command for CSV ingestion:
```shell
python pipeline.py \
    --project $PROJECT_ID \
    --region $DATAFLOW_REGION \
    --input gs://na_data_internal/sample_file/sample_data.csv \
    --output $DATASET_NAME.csv_output \
    --schema ID:STRING,Name:STRING,Date:STRING,Value:STRING \
    --runner DataflowRunner \
    --temp_location gs://$BUCKET_NAME/tmp/
```

