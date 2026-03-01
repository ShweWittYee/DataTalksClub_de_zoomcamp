import dlt
from dlt.sources.rest_api import rest_api_source


def taxi_source():
    """A simple REST API source that fetches NYC taxi records one page at a time.

    The service returns a list of up to 1000 trips per request.  Pages are selected
    with the ``page`` query parameter.  Pagination stops automatically when an
    empty list is returned (the default behaviour of the ``page_number``
    paginator).
    """
    return rest_api_source({
        "client": {
            "base_url": "https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api",
        },
        # apply sensible defaults to every resource
        "resource_defaults": {
            # no reliable natural primary key in the data, just append each run
            "write_disposition": "append",
        },
        "resources": [
            {
                "name": "trips",
                "endpoint": {
                    # hit the root of the service
                    "path": "",
                    # the response is a top‑level array of records; no selector
                    # is required (array will be iterated automatically)
                    "paginator": {
                        "type": "page_number",
                        "page_param": "page",
                        "base_page": 1,
                        # API returns a bare list, so there is no `total` field.
                        # disable the total check and rely on stop_after_empty_page
                        "total_path": None,
                        # stop when an empty page is seen (default behaviour)
                        "stop_after_empty_page": True,
                    },
                },
            },
        ],
    })


pipeline = dlt.pipeline(
    pipeline_name="taxi_pipeline",
    destination="duckdb",
    progress=None,  # use default (no progress output)
)


if __name__ == "__main__":
    load_info = pipeline.run(taxi_source())
    # show small summary instead of entire object (avoids huge dump)
    print(f"run successful, loads: {load_info.loads_ids}")  # noqa: T201
