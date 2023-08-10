#!/usr/bin/env python

"""Example extractor based on the clowder code."""
import pandas as pd
import json
import os
import csv
import types
import pickle

import logging
from pyclowder.extractors import Extractor
import pyclowder.files

from algorithm import algorithm


def save_local_output(localSavePath, fname, output_data):
    """
    save output in memory first to local file
    :param localSavePath: local saved file
    :param remoteSavePath: remote save file path
    :param fname: filename
    :param output_data: the actual data
    :return: local saved file path
    """
    # json
    if isinstance(output_data, dict):
        fname += '.json'
        with open(os.path.join(localSavePath, fname), 'w') as f:
            json.dump(output_data, f)

    # dataframe to csv
    elif isinstance(output_data, pd.DataFrame):
        fname += '.csv'
        output_data.to_csv(fname, encoding='utf-8')

    # string to html
    elif isinstance(output_data, str):
        fname += '.html'
        with open(os.path.join(localSavePath, fname), 'w') as f:
            f.write(output_data)

    # list(list) to csv
    elif isinstance(output_data, list) \
            and (isinstance(output_data[0], list) or isinstance(output_data[0],
                                                                tuple)):
        fname += '.csv'
        with open(os.path.join(localSavePath, fname), 'w', newline='',
                  encoding='utf-8') as f:
            writer = csv.writer(f)
            for row in output_data:
                try:
                    writer.writerow(row)
                except UnicodeEncodeError as e:
                    print(e)

    # special case
    elif isinstance(output_data, types.GeneratorType):
        if fname == 'gephi':
            fname += '.gml'
        elif fname == 'pajek':
            fname += '.net'
        else:
            fname += '.unknown'

        with open(os.path.join(localSavePath, fname), 'w', newline='',
                  encoding='utf-8') as f:
            for line in output_data:
                f.write(line + '\n')

    # else pickle the object
    else:
        fname += '.pickle'
        with open(os.path.join(localSavePath, fname), 'wb') as f:
            pickle.dump(output_data, f)

    return os.path.join(localSavePath, fname)


class SmmExtractor(Extractor):
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
        # Parse user parameters to determine which column to analyze
        userParams = parameters.get('parameters')
        output = algorithm(df, userParams)
        connector.message_process(resource, "Running the algorithm...")

        # upload object to s3 bucket and return the url
        for fname, output_data in output.items():
            if fname != 'uid':
                local_output_path = save_local_output("", fname, output_data)
                uploaded_file_id = pyclowder.files.upload_to_dataset(connector, host, secret_key, dataset_id,
                                                                 local_output_path)
                connector.message_process(resource, "Saving " + local_output_path + "...")

                # write params to metadata
                metadata = self.get_metadata(userParams, 'file', uploaded_file_id, host)
                pyclowder.files.upload_metadata(connector, host, secret_key, uploaded_file_id, metadata)
                connector.message_process(resource, "Writing metadata...")


if __name__ == "__main__":
    extractor = SmmExtractor()
    extractor.start()
