import requests
import re

class image_crawler:

    @staticmethod
    def crawler(url):
        r = requests.get(url, stream=True)

        # get filename
        if "Content-Disposition" in r.headers.keys():
            fname = re.findall("filename=(.+)", r.headers["Content-Disposition"])[
                0]
        else:
            fname = url.split("/")[-1]

        return fname, r.content

    @staticmethod
    def is_image(url):
        head = requests.head(url)
        content_type = head.headers.get('content-type')

        if content_type is not None and content_type.lower().startswith('image'):
            return True
        else:
            return False


if __name__ == "__main__":

    url = "https://theweek.com/speedreads-amp/807154/trump-putin-plan-meeting-argentina"
    if image_crawler.is_image(url):
        fname, binary = image_crawler.crawler(url)



