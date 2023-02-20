import argparse
from simpletransformers.classification import MultiLabelClassificationModel
import pandas as pd
import json

from notification import notification
import os
import writeToS3 as s3


def multiple_sentences(df, model):

    if 'text' in df.columns:
        to_predict = df.text.apply(lambda x: x.replace('\n', ' ')).tolist()
        preds, probs = model.predict(to_predict)
        sub_df = pd.DataFrame(probs, columns=['sophistication','excitement','sincerity','competence','ruggedness'])

        df['sophistication'] = sub_df['sophistication']
        df['excitement'] = sub_df['excitement']
        df['sincerity'] = sub_df['sincerity']
        df['competence'] = sub_df['competence']
        df['ruggedness'] = sub_df['ruggedness']

        return df

    else:
        raise ValueError("There is no 'text' field in given CSV file.")


def average(df):
    sophistication = df['sophistication'].mean()
    excitement = df['excitement'].mean()
    sincerity = df['sincerity'].mean()
    competence = df['competence'].mean()
    ruggedness = df['ruggedness'].mean()

    return {
        "sophistication": float(sophistication),
        "excitement": float(excitement),
        "sincerity": float(sincerity),
        "competence": float(competence),
        "ruggedness": float(ruggedness)
    }


if __name__ == '__main__':

    # entrance to invoke Batch
    urls = {}

    # default parameters
    parser = argparse.ArgumentParser(description="processing...")
    parser.add_argument('--sessionID', required=True)
    parser.add_argument('--screen_name', required=True)
    parser.add_argument('--email', required=True)
    parser.add_argument('--sessionURL', required=True)

    # user specified parameters
    parsed, unknown = parser.parse_known_args()
    for arg in unknown:
        if arg.startswith("--"):
            parser.add_argument(arg, required=False)

    params = vars(parser.parse_args())


    awsPath = os.path.join(params['sessionID'], params['screen_name'])
    localPath = os.path.join('/tmp', params['sessionID'], params['screen_name'])
    if not os.path.exists(localPath):
        os.makedirs(localPath)
    screen_name = params['screen_name']

    try:
        s3.downloadToDisk(screen_name + '_tweets.txt', localPath, awsPath)
    except:
        raise ValueError('Cannot find the timeline in the remote storage!')

    # calculate brand personality
    model = MultiLabelClassificationModel('roberta', 'checkpoint-17315-epoch-5', num_labels=5,
                                          args={"reprocess_input_data": True, 'use_cached_eval_features': False},
                                          use_cuda=False)
    df = pd.read_csv(os.path.join(localPath, screen_name + '_tweets.txt'), error_bad_lines=False)
    new_df = multiple_sentences(df, model)
    fname_sentences = screen_name + '_utku_personality_sentences.csv'
    new_df.to_csv(os.path.join(localPath, fname_sentences), index=False)
    s3.upload(localPath, awsPath, fname_sentences)

    # get the average score
    mean_metrics = average(new_df)
    fname_average = screen_name + '_utku_personality_average.json'
    with open(os.path.join(localPath, fname_average), 'w') as f:
        json.dump(mean_metrics, f)
    s3.upload(localPath, awsPath, fname_average)

    # push notification email
    notification(toaddr=params['email'], sessionURL=params['sessionURL'])
