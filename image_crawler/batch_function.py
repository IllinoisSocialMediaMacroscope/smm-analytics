import dataset
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
    params = vars(parser.parse_args())

    # arranging the paths
    path = dataset.organize_path_lambda(params)

    # prepare input dataset
    df = dataset.get_remote_input(path['remoteReadPath'],
                                  path['filename'],
                                  path['localReadPath'])

    img_urls = []
    source = path['remoteReadPath'].split('/')[-3]
    if source == "reddit-Search" or source == "reddit-Post" \
            or source == "crimson-Hexagon":
        img_urls = df['url'].tolist()
    elif source == "twitter-Tweet" or source == "twitter-Timeline":
        pass
    elif source == "twitter-Stream":
        pass
    elif source == "reddit-Historical-Post":
        img_urls = df['_source.url'].tolist()
    else:
        raise ValueError("This data source does not support image!")

    urls = {}
    for img_url in img_urls:
        if ic.is_image(img_url):
            filename, binary = ic.crawler(img_url)
            dataset.save_local_output(path['localSavePath'], filename, binary)
    urls['images.zip'] = dataset.save_remote_output(
        path['localSavePath'], path['remoteSavePath'], 'images.zip')

    # push notification email
    notification(toaddr=params['email'], case=3,
                 filename=path['remoteSavePath'],
                 links=urls, sessionURL=params['sessionURL'])
