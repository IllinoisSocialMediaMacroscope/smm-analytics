import csv
import os
import json
import pickle
import pandas as pd
import types


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

    return os.path.join(localpath, filename)
