import argparse
import csv
import os
import shutil
import uuid
import zipfile

import notification as n
import pandas as pd
import praw
import writeToS3 as s3


def deletedir(dir):
    shutil.rmtree(dir)


def getFolderSize(folder):
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += getFolderSize(itempath)
    return total_size


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), file)


def bfs(submission, id, directory):
    # expand comments
    submission.comments.replace_more(limit=None)
    comment_queue = submission.comments[:]  # Seed with top-level
    comments_no_order = [['author', 'body', 'created_utc', 'id', 'link_id',
                          'parent_id', 'score', 'subreddit_display_name', 'subreddit_name_prefixed', 'subreddit_id']]
    while comment_queue:
        comment = comment_queue.pop(0)
        comments_no_order.append([str(comment.author),
                                  comment.body, comment.created_utc, comment.id, comment.link_id,
                                  comment.parent_id, comment.score, comment.subreddit.display_name,
                                  comment.subreddit_name_prefixed, comment.subreddit_id])
        comment_queue.extend(comment.replies)

    # save to csv
    with open(os.path.join(directory, id + '.csv'), 'w', newline="", encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=',')
        for c in comments_no_order:
            try:
                writer.writerow(c)
            except:
                print('encoding error')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Processing...")
    parser.add_argument('--email', required=True)
    parser.add_argument('--remoteReadPath', required=True)
    parser.add_argument('--s3FolderName', required=True)
    parser.add_argument('--sessionURL', required=True)
    args = parser.parse_args()

    uid = str(uuid.uuid4())
    temp_dir = os.path.join('/tmp', args.s3FolderName, uid)
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # configure output directory
    # save it in download/temp/xxx-xxxxxxxxxxxxx-xxxxx/aww-comments

    file = args.remoteReadPath.split('/')[-2]
    fname_zip = file + '.zip'
    comments_folder = os.path.join(temp_dir, file + '-comments')
    if not os.path.exists(comments_folder):
        os.makedirs(comments_folder)

    s3.downloadToDisk(filename=file + '.csv', localpath=temp_dir, remotepath=args.remoteReadPath)
    Array = []
    try:
        with open(os.path.join(temp_dir, file + '.csv'), 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            try:
                for row in reader:
                    Array.append(row)
            except Exception as e:
                pass

    except:
        with open(os.path.join(temp_dir, file + '.csv'), 'r', encoding="ISO-8859-1") as f:
            reader = csv.reader(f)
            try:
                for row in reader:
                    Array.append(row)
            except Exception as e:
                pass

    df = pd.DataFrame(Array[1:], columns=Array[0])
    headers = df.columns.values.tolist()
    if 'permalink' in headers and 'id' in headers:
        urls = df['permalink'].dropna().astype('str').tolist()
        ids = df['id'].dropna().astype('str').tolist()
    elif '_source.permalink' in headers and '_source.id' in headers:
        urls = df['_source.permalink'].dropna().astype('str').tolist()
        ids = df['_source.id'].dropna().astype('str').tolist()
    else:
        deletedir('/tmp')
        n.notification(args.email, case=0, filename='', links='', sessionURL=args.sessionURL)
        raise ValueError('The Reddit post collection provided does not have permalink and/or id in it.')

    # praw construct submission           
    reddit = praw.Reddit(user_agent='Comment Extraction (by /u/USERNAME)',
                         client_id=os.environ['REDDIT_CLIENT_ID'], client_secret=os.environ['REDDIT_CLIENT_SECRET'])

    # loop through the id and store their comments
    for url, id in zip(urls, ids):
        url = "https://www.reddit.com" + url
        try:
            submission = reddit.submission(url=url)
            bfs(submission, id, comments_folder)
        except:
            print("The url " + url + " is not valid.")

    # success and send email notification
    # zip goes here
    zipf = zipfile.ZipFile(os.path.join(temp_dir, fname_zip), 'w')
    zipdir(comments_folder, zipf)
    zipf.close()

    # upload this zip to the s3 corresponding folder
    s3.upload(temp_dir, args.remoteReadPath, fname_zip)
    url = s3.generate_downloads(args.remoteReadPath, fname_zip)

    # delete the files
    deletedir('/tmp')

    # send out email notification
    n.notification(args.email, case=2, filename=args.remoteReadPath, links=url, sessionURL=args.sessionURL)
