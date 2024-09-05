import re
from pydantic import BaseModel, ValidationError, Field
import apache_beam as beam
from apache_beam.io.textio import ReadFromCsv, ReadFromJson
from apache_beam.io.parquetio import ReadFromParquet
from apache_beam.io.gcp.bigquery import WriteToBigQuery
from apache_beam.options.pipeline_options import PipelineOptions


class CustomOptions(PipelineOptions):
    @classmethod
    # Define a custom pipeline option that specfies the Cloud Storage bucket.
    def _add_argparse_args(cls, parser):
        parser.add_argument("--input", required=True)
        parser.add_argument("--output", required=True)
        parser.add_argument("--schema", required=False)


class InputFormatSettings(BaseModel):
    filename: str = Field(pattern=r".*\.(csv|json|txt|parquet)$")


class ConvertTupledToDict(beam.DoFn):
    def process(self, element):
        if not isinstance(element, dict):
            element = element._asdict()
        string_dict = {key: str(value) for key, value in element.items()}
        yield string_dict


class DataIngestionDataflow:
    def __init__(self, options):
        # Parse the pipeline options passed into the application.
        self.options = options

    def run(self):
        try:
            # Verify if input file is supported input format
            input_file = InputFormatSettings.model_validate(
                {"filename": self.options.input}
            )

            # Run the data pipeline with pipeline options.
            with beam.Pipeline(options=self.options) as pipeline:
                if re.match(".*\.csv$", input_file.filename):
                    read_stage = pipeline | "Read CSV" >> ReadFromCsv(
                        input_file.filename
                    )
                elif re.match(".*(json|txt)$", input_file.filename):
                    read_stage = pipeline | "Read JSON" >> ReadFromJson(
                        input_file.filename
                    )
                elif re.match(".*\.parquet$", input_file.filename):
                    read_stage = pipeline | "Read Parquet" >> ReadFromParquet(
                        input_file.filename
                    )

                (
                    read_stage
                    | "Change all data types into string"
                    >> beam.ParDo(ConvertTupledToDict())
                    | "Write to BigQuery"
                    >> WriteToBigQuery(
                        options.output,
                        schema=options.schema,
                        write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
                        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                    )
                )
        except ValidationError as e:
            print(f"Unsupported input format: {e.errors}")


if __name__ == "__main__":
    options = CustomOptions()
    pipeline = DataIngestionDataflow(options)
    pipeline.run()
