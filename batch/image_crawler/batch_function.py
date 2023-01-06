from dataset import Dataset
import argparse
from notification import notification
from image_crawler import image_crawler as ic

if __name__ == '__main__':

    # entrance to invoke Batch
    urls = {}

    # default parameters
    parser = argparse.ArgumentParser(description="processing...")
    parser.add_argument('--remoteReadPath', required=True)
    parser.add_argument('--email', required=True)
    parser.add_argument('--sessionURL', required=True)

    # user specified parameters
    parsed, unknown = parser.parse_known_args()
    for arg in unknown:
        if arg.startswith("--"):
            parser.add_argument(arg, required=False)


    params = vars(parser.parse_args())

    if 'HOST_IP' in params.keys():
        HOST_IP = params['HOST_IP']
        params.pop('HOST_IP', None)
    else:
        HOST_IP = None

    if 'AWS_ACCESSKEY' in params.keys():
        AWS_ACCESSKEY = params['AWS_ACCESSKEY']
        params.pop('AWS_ACCESSKEY', None)
    else:
        AWS_ACCESSKEY = None

    if 'AWS_ACCESSKEYSECRET' in params.keys():
        AWS_ACCESSKEYSECRET = params['AWS_ACCESSKEYSECRET']
        params.pop('AWS_ACCESSKEYSECRET', None)
    else:
        AWS_ACCESSKEYSECRET = None

    if 'BUCKET_NAME' in params.keys():
        BUCKET_NAME = params['BUCKET_NAME']
        params.pop('BUCKET_NAME', None)
    else:
        BUCKET_NAME = None

    d = Dataset(HOST_IP, AWS_ACCESSKEY, AWS_ACCESSKEYSECRET, BUCKET_NAME)

    # arranging the paths
    path = d.organize_path_lambda(params)

    # prepare input dataset
    df = d.get_remote_input(path['remoteReadPath'],
                                  path['filename'],
                                  path['localReadPath'])

    img_urls = []
    source = path['remoteReadPath'].split('/')[-3]
    if source == "reddit-Search" or source == "reddit-Post" \
            or source == "crimson-Hexagon" or source == "reddit-Historical-Post"\
            and 'url' in list(df.columns):
        img_urls = df['url'].dropna().tolist()

    elif source == "twitter-Tweet" or source == "twitter-Timeline" \
            and 'entities.media.media_url' in list(df.columns):
        img_urls = df['entities.media.media_url'].dropna().tolist()

    elif source == 'flickr-Photo' and 'size.source' in list(df.columns):
        img_urls = df['size.source'].dropna().tolist()

    else:
        raise ValueError("This data source does not support image collection!")

    urls = {}
    for img_url in img_urls:
        if ic.is_image(img_url):
            filename, binary = ic.crawler(img_url)
            d.save_local_output(path['localSavePath'], filename, binary)
    urls['images.zip'] = d.save_remote_output(
        path['localSavePath'], path['remoteSavePath'], 'images.zip')

    # push notification email
    notification(toaddr=params['email'], case=3,
                 filename=path['remoteSavePath'],
                 links=urls, sessionURL=params['sessionURL'])
