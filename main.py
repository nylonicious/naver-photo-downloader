import asyncio
import os
from sys import version_info
from urllib.parse import urlparse

import aiohttp


class NaverDownloader:
    def __init__(self, url, tags):
        self.session = None
        asyncio.run(self.queue_downloads(tags, url))

    async def queue_downloads(self, tags, url):
        tasks = []
        cid = urlparse(url).path.split('/')[3]
        desiredpath = os.path.join(os.getcwd(), cid)
        if not os.path.exists(desiredpath):
            os.makedirs(desiredpath)
        page = True
        counter = 1
        item_list_url = 'https://entertain.naver.com/photo/issueItemList.json'
        timeout = aiohttp.ClientTimeout(total=60)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'}
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as self.session:
            while page:
                async with self.session.get(item_list_url, params={'page': counter, 'cid': cid}) as response:
                    data = await response.json()
                    page = data['results'][0]['thumbnails']
                    counter += 1
                    for i in page:
                        url = i['thumbUrl']
                        title = i['title']
                        picture_url = url.split('?')[0]
                        picture_name = urlparse(picture_url).path.split('/')[-1]
                        picture_path = os.path.join(desiredpath, picture_name)
                        for item in tags:
                            if not os.path.isfile(picture_path) and item in title:
                                tasks.append(asyncio.create_task(self.download(picture_url, picture_path)))
            await asyncio.gather(*tasks)

    async def download(self, picture_url, picture_path):
        async with self.session.get(picture_url) as r:
            if r.status == 200:
                with open(picture_path, 'wb') as f:
                    f.write(await r.read())
                    print(f'Downloading {picture_url}')
            else:
                print(f'Error {r.status} while getting request for {picture_url}')


def main():
    url = input('Enter url you wish to download images from: ')
    tags = [str(i) for i in input('Enter space separated tags: ').split()]
    if not tags:
        tags = ['']
    NaverDownloader(url, tags)


if __name__ == '__main__':
    assert version_info >= (3, 7), 'Script requires Python 3.7+.'
    main()
