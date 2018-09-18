try:
    import asyncio  
    import aiohttp
    import aiofiles
except ImportError:
    ASYNC_INSTALLED = False
    pass
else:
    ASYNC_INSTALLED = True
    from aiohttp import ClientSession

try:
    import requests
except ImportError:
    pass

try:
    from timeit import default_timer
except:
    pass


base_url = 'http://stats.nba.com/stats'
HEADERS = {
    'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/45.0.2454.101 Safari/537.36'),
}

async def get_players(player_args):
    endpoint = '/commonallplayers'
    params = {'leagueid': '00', 'season': '2016-17', 'isonlycurrentseason': '1'}
    url = f'{base_url}{endpoint}'
    print('Getting all players...')
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS, params=params) as resp:
            data = await resp.json()
    player_args.extend(
        [(item[0], item[2]) for item in data['resultSets'][0]['rowSet']])

async def get_player(player_id, player_name):
    endpoint = '/commonplayerinfo'
    params = {'playerid': player_id}
    url = f'{base_url}{endpoint}'
    print(f'Getting player {player_name}')
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS, params=params) as resp:
            print(resp)
            data = await resp.text()
    async with aiofiles.open(
            f'{player_name.replace(" ", "_")}.json', 'w') as file:
        await file.write(data)

loop = asyncio.get_event_loop()
player_args = []
loop.run_until_complete(get_players(player_args))
loop.run_until_complete(
    asyncio.gather(
        *(get_player(*args) for args in player_args)
    )
)



async def compute(x, y):
    print("Compute %s + %s ..." % (x, y))
    await asyncio.sleep(1.0)
    return x + y

async def print_sum(x, y):
    result = await compute(x, y)
    print("%s + %s = %s" % (x, y, result))

loop = asyncio.get_event_loop()
loop.run_until_complete(print_sum(1, 2))
loop.close()


try:
    assert ASYNC_INSTALLED
except:
    # https://gist.github.com/debugtalk/3d26581686b63c28227777569c02cf2c
    def fetch_page(url, idx):  
        url = 'https://yahoo.com'
        response = yield from aiohttp.request('GET', url)
    
        if response.status == 200:
            print("data fetched successfully for: %d" % idx)
        else:
            print("data fetch failed for: %d" % idx)
            print(response.content, response.status)
    
    def main():  
        url = 'https://yahoo.com'
        urls = [url] * 100
    
        coros = []
        for idx, url in enumerate(urls):
            coros.append(asyncio.Task(fetch_page(url, idx)))
    
        yield from asyncio.gather(*coros)
    
#    if __name__ == '__main__':  
#        loop = asyncio.get_event_loop()
#        loop.run_until_complete(main())
    
    
# https://pawelmhm.github.io/asyncio/python/aiohttp/2016/04/22/asyncio-aiohttp.html

async def my_fetch(url, session):
    async with session.get(url) as response:
        return await response.read()

async def run(r):
    url = "http://localhost:8080/{}"
    tasks = []

    # Fetch all responses within one Client session,
    # keep connection alive for all requests.
    async with ClientSession() as session:
        for i in range(r):
            task = asyncio.ensure_future(my_fetch(url.format(i), session))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        # you now have all response bodies in this variable
        print(responses)

def print_responses(result):
    print(result)

loop = asyncio.get_event_loop()
future = asyncio.ensure_future(run(4))
loop.run_until_complete(future)

# http://mahugh.com/2017/05/23/http-requests-asyncio-aiohttp-vs-requests/
# https://gist.github.com/dmahugh/b043ecbc4c61920aa685e0febbabb959

def demo_sequential(urls):
    """Fetch list of web pages sequentially.
    """
    start_time = default_timer()
    for url in urls:
        start_time_url = default_timer()
        _ = requests.get(url)
        elapsed = default_timer() - start_time_url
        print('{0:30}{1:5.2f} {2}'.format(url, elapsed, asterisks(elapsed)))
    tot_elapsed = default_timer() - start_time
    print(' TOTAL SECONDS: '.rjust(30, '-') + '{0:5.2f} {1}'. \
        format(tot_elapsed, asterisks(tot_elapsed)) + '\n')

def demo_async(urls):
    """Fetch list of web pages asynchronously."""
    start_time = default_timer()

    loop = asyncio.get_event_loop() # event loop
    future = asyncio.ensure_future(fetch_all(urls)) # tasks to do
    loop.run_until_complete(future) # loop until done

    tot_elapsed = default_timer() - start_time
    print(' WITH ASYNCIO: '.rjust(30, '-') + '{0:5.2f} {1}'. \
        format(tot_elapsed, asterisks(tot_elapsed)))

async def fetch_all(urls):
    """Launch requests for all web pages."""
    tasks = []
    fetch.start_time = dict() # dictionary of start times for each url
    async with ClientSession() as session:
        for url in urls:
            task = asyncio.ensure_future(fetch(url, session))
            tasks.append(task) # create list of tasks
        _ = await asyncio.gather(*tasks) # gather task responses

async def get_status(url, session):
    async with session.head(url) as response:
        try:
            await response.raise_for_status()
        except:
            raise IOError('wrong request formulated')  
        else:
            status = await response.status_code
            await response.close()
    return status


async def fetch(url, session):
    """Fetch a url, using specified ClientSession."""
    fetch.start_time[url] = default_timer()
    async with session.get(url) as response:
        resp = await response.read()
        elapsed = default_timer() - fetch.start_time[url]
        print('{0:30}{1:5.2f} {2}'.format(url, elapsed, asterisks(elapsed)))
        return resp

def asterisks(num):
    """Returns a string of asterisks reflecting the magnitude of a number."""
    return int(num*10)*'*'

if __name__ == '__main__':
    # asyncio.set_event_loop(asyncio.new_event_loop())
    URL_LIST = ['https://facebook.com',
                'https://github.com',
                'https://google.com',
                'https://microsoft.com',
                'https://yahoo.com']
    demo_sequential(URL_LIST)
    demo_async(URL_LIST)
    
    

async def fetch1(session, url):
    async with session.get(url) as response:
        return await response.text()

async def main1():
    urls = [
            'http://python.org',
            'https://google.com',
            'http://yifei.me'
        ]
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            tasks.append(fetch1(session, url))
        htmls = await asyncio.gather(*tasks)
        for html in htmls:
            print(html[:100])

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main1())
    
    
# https://medium.com/python-pandemonium/asyncio-coroutine-patterns-beyond-await-a6121486656f    
    

@asyncio.coroutine 
def fetch2(session, url):
    response = yield from session.get(url)
    text = yield from response.text()
    return text

@asyncio.coroutine 
def main2():
    session = aiohttp.ClientSession()
    urls = [
            'http://python.org',
            'https://google.com',
            'http://yifei.me'
        ]
    tasks = []
    for url in urls:
        tasks.append(fetch2(session, url))
    htmls = yield from asyncio.gather(*tasks)
    for html in htmls:
        print('---------------')
        print(html[:100])
    yield from session.close()
    return htmls

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(main2())


import aiohttp
import asyncio
import async_timeout
import os
 
async def download_coroutine(session, url):
    with async_timeout.timeout(10):
        async with session.get(url) as response:
            filename = os.path.basename(url)
            with open(filename, 'wb') as f_handle:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    f_handle.write(chunk)
            return await response.release()
 
async def main3(loop):
    urls = ["http://www.irs.gov/pub/irs-pdf/f1040.pdf",
        "http://www.irs.gov/pub/irs-pdf/f1040a.pdf",
        "http://www.irs.gov/pub/irs-pdf/f1040ez.pdf",
        "http://www.irs.gov/pub/irs-pdf/f1040es.pdf",
        "http://www.irs.gov/pub/irs-pdf/f1040sb.pdf"]
 
    async with aiohttp.ClientSession(loop=loop) as session:
        tasks = [download_coroutine(session, url) for url in urls]
        await asyncio.gather(*tasks)
 
asyncio.set_event_loop(asyncio.new_event_loop())
loop = asyncio.get_event_loop()
loop.run_until_complete(main3(loop))


import asyncio
async def mycoro(number):
    print("Starting %d" % number)
    await asyncio.sleep(1)
    print("Finishing %d" % number)
    return str(number)
asyncio.set_event_loop(asyncio.new_event_loop())
several_futures = asyncio.gather(
    mycoro(1), mycoro(2), mycoro(3))
loop = asyncio.get_event_loop()
res = loop.run_until_complete(several_futures)
loop.close()