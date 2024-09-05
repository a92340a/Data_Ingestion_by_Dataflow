import re
import json
import logging
import argparse
from pydantic import BaseModel, ValidationError, Field
from google.cloud import storage
import apache_beam as beam
from apache_beam.io.textio import ReadFromCsv
from apache_beam.io.gcp.bigquery import WriteToBigQuery
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions

# Configure logging
logging.basicConfig(level=logging.INFO)


class InputFormatSettings(BaseModel):
    filename: str = Field(pattern=r".*\.(csv)$")


class ConvertTupledToDict(beam.DoFn):
    def process(self, element):
        if not isinstance(element, dict):
            element = element._asdict()
        string_dict = {key: str(value) for key, value in element.items()}
        yield string_dict


def _load_schema(gcs_path):
    bucket_name, blob_name = gcs_path[5:].split("/", 1)
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    json_data = blob.download_as_text()

    data_dict = {"fields": json.loads(json_data)}
    return data_dict


def run(argv=None):
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Dataflow Flex Template Pipeline")
    parser.add_argument("--inputFilePath", required=True, help="Input file path")
    parser.add_argument("--outputTable", required=True, help="Output BigQuery dataset and table")
    parser.add_argument(
        "--schemaJSONPath", help="Table schema compiled with 'column1:datatype1,column2:datatyp2e' pattern"
    )
    parser.add_argument("--chunkSize", type=int, default=5000, help="Number of lines to read from the file per chunk")
    parser.add_argument("--csvFileEncoding", default="utf-8", help="The CSV file character encoding format.")
    parser.add_argument("--isTruncate", default="false", help="The CSV file character encoding format.")

    # known_args: These are the arguments that the script knows about (defined by add_argument calls
    # pipeline_args: There are extra arguments that argparse does not recognize, and pass the GCP default parameters by GoogleCloudOptions
    known_args, pipeline_args = parser.parse_known_args(argv)

    options = PipelineOptions(pipeline_args)
    options.view_as(GoogleCloudOptions)

    # Verify if input file is supported input format
    try:
        InputFormatSettings.model_validate({"filename": known_args.inputFilePath})
    except ValidationError as e:
        logging.error(f"Unsupported input format: {e.errors}")
        raise

    with beam.Pipeline(options=options) as pipeline:
        (
            pipeline
            | "Read CSV"
            >> ReadFromCsv(
                known_args.inputFilePath,
                chunksize=known_args.chunkSize,
                encoding=known_args.csvFileEncoding,
            )
            | "Change all data types into string" >> beam.ParDo(ConvertTupledToDict())
            | "Write to BigQuery"
            >> WriteToBigQuery(
                known_args.outputTable,
                schema=_load_schema(known_args.schemaJSONPath),
                write_disposition=(
                    beam.io.BigQueryDisposition.WRITE_TRUNCATE
                    if known_args.isTruncate == "true"
                    else beam.io.BigQueryDisposition.WRITE_APPEND
                ),
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            )
        )


if __name__ == "__main__":
    run()
