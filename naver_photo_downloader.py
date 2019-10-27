import asyncio
from pathlib import Path
from sys import version_info
from urllib.parse import urlparse

import aiohttp


async def queue_downloads(url, tags):
    tasks = []
    cid = urlparse(url).path.split('/')[3]
    desired_path = Path.cwd() / cid
    desired_path.mkdir(parents=False, exist_ok=True)
    page = True
    counter = 1
    item_list_url = 'https://entertain.naver.com/photo/issueItemList.json'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0'}
    async with aiohttp.ClientSession(headers=headers) as session:
        while page:
            async with session.get(item_list_url, params={'page': counter, 'cid': cid}) as response:
                data = await response.json()
                page = data['results'][0]['thumbnails']
                counter += 1
                for item in page:
                    url = item['thumbUrl']
                    title = item['title']
                    picture_url = url.split('?')[0]
                    picture_name = urlparse(picture_url).path.split('/')[-1]
                    picture_path = desired_path / picture_name
                    for item in tags:
                        if not picture_path.is_file() and item in title:
                            tasks.append(asyncio.create_task(download(session, picture_url, picture_path)))
                await asyncio.gather(*tasks)


async def download(session, picture_url, picture_path):
    async with session.get(picture_url) as r:
        if r.status == 200:
            picture_path.write_bytes(await r.read())
            print(f'Downloaded {picture_url}')
        else:
            print(f'Error {r.status} while getting request for {picture_url}')


def main():
    url = input('Enter url you wish to download images from: ')
    tags = [str(i) for i in input('Enter space separated tags: ').split()]
    if not tags:
        tags = ['']
    asyncio.run(queue_downloads(url, tags))


if __name__ == '__main__':
    assert version_info >= (3, 7), 'Script requires Python 3.7+.'
    main()
