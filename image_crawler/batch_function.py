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
    parser.add_argument('--column', required=True)
    parser.add_argument('--s3FolderName', required=True)
    parser.add_argument('--uid', required=True)
    parser.add_argument('--resultPath', required=True)
    parser.add_argument('--email', required=True)
    parser.add_argument('--sessionURL', required=True)

    # user specified parameters
    parsed, unknown = parser.parse_known_args()
    for arg in unknown:
        if arg.startswith("--"):
            parser.add_argument(arg, required=False)

    params = vars(parser.parse_args())

    # arranging the paths
    path = dataset.organize_path_lambda(params)

    # prepare input dataset
    df = dataset.get_remote_input(path['remoteReadPath'],
                                  path['filename'],
                                  path['localReadPath'])

    img_urls = []
    if params['source'] == "reddit-Search":
        img_urls = df['url'].tolist()
    elif params['source'] == "":
        pass
    elif params['source'] == "":
        pass
    elif params['source'] == "":
        pass

    urls = {}
    for img_url in img_urls:
        if ic.is_image(img_url):
            fname, binary = ic.crawler(img_url)
            urls[fname] = dataset.save_remote_output(path['localSavePath'],
                                       path['remoteSavePath'],
                                       fname,
                                       binary)
    # push notification email
    notification(toaddr=params['email'], case=3, filename=path['remoteSavePath'],
                 links=urls, sessionURL=params['sessionURL'])
