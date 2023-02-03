#!/usr/bin/env python

"""Example extractor based on the clowder code."""
import dataset
import pandas as pd

import logging
from pyclowder.extractors import Extractor
import pyclowder.files

from algorithm import algorithm


class SentimentAnalysisExtractor(Extractor):
    """Count the number of characters, words and lines in a text file."""
    def __init__(self):
        Extractor.__init__(self)

        # parse command line and load default logging configuration
        self.setup()

        # setup logging for the exctractor
        logging.getLogger('pyclowder').setLevel(logging.DEBUG)
        logging.getLogger('__main__').setLevel(logging.DEBUG)

    def process_message(self, connector, host, secret_key, resource, parameters):
        # this extractor runs on dataset
        # uncomment to see the resource
        logger = logging.getLogger(__name__)
        inputfile = resource["local_paths"][0]
        dataset_id = resource['parent'].get('id')

        df = pd.read_csv(inputfile)
        connector.message_process(resource, "Loading contents of file...")

        # execute the algorithm
        # TODO figure out how to pass in parameters
        params = {'column':'text',
                  'algorithm': 'vader'}
        output = algorithm(df, params)
        connector.message_process(resource, "Running the algorithm...")

        # upload object to s3 bucket and return the url
        for fname, output_data in output.items():
            if fname != 'uid':
                local_output_path = dataset.save_local_output("", fname, output_data)
                pyclowder.files.upload_to_dataset(connector, host, secret_key, dataset_id, local_output_path)
                connector.message_process(resource, "Saving " + local_output_path + "...")


if __name__ == "__main__":
    extractor = SentimentAnalysisExtractor()
    extractor.start()
