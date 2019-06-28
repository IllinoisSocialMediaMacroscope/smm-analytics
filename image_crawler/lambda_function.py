import dataset
from image_crawler import image_crawler as ic

def lambda_handler(params, context):
    '''
    entrance to invoke AWS lambda,
    variable params contains parameters passed in
    '''
    urls = {}

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

    urls = []
    for img_url in img_urls:
        if ic.is_image(img_url):
            fname, binary = ic.crawler(img_url)
            urls[fname] = dataset.save_remote_output(path['localSavePath'],
                                                   path['remoteSavePath'],
                                                   fname,
                                                   binary)
    return urls
