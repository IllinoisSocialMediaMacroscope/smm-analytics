import pandas as pd
from simpletransformers.classification import MultiLabelClassificationModel


def multiple_sentences(df, model):
    if 'text' in df.columns:
        to_predict = df.text.apply(lambda x: x.replace('\n', ' ')).tolist()
        preds, probs = model.predict(to_predict)
        sub_df = pd.DataFrame(probs, columns=['sophistication', 'excitement', 'sincerity', 'competence', 'ruggedness'])

        df['sophistication'] = sub_df['sophistication']
        df['excitement'] = sub_df['excitement']
        df['sincerity'] = sub_df['sincerity']
        df['competence'] = sub_df['competence']
        df['ruggedness'] = sub_df['ruggedness']

        return df

    else:
        raise ValueError("There is no 'text' field in given CSV file.")


class Personality:

    def __init__(self, df, column):

        if 'id_str' in df.columns:
            self.id_column = 'id_str'
        elif 'id' in df.columns:
            self.id_column = 'id'
        elif 'comment_id' in df.columns:
            self.id_column = 'comment_id'
        elif '_source.id_str':
            self.id_column = '_source.id_str'
        elif '_source.id':
            self.id_column = '_source.id_str'
        else:
            self.id_column = "id"

        self.df_new = df[df[column] != ''][[self.id_column, column]].dropna()

    def predict(self, algorithm):
        # TODO when multiple algorithms available, implement multiple algorithms here use the condition algorithm
        model = MultiLabelClassificationModel('roberta', 'checkpoint-17315-epoch-5', num_labels=5,
                                              args={"reprocess_input_data": True, 'use_cached_eval_features': False},
                                              use_cuda=False)
        df_predict = multiple_sentences(self.df_new, model)

        return df_predict

    @staticmethod
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
