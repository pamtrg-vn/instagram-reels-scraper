from typing import Optional, List, Callable, Dict, Generator
import requests
import json
import argparse
import requests.sessions 

# Custom exception classes
class IGException(Exception):
    pass

class IGNetWorkException(Exception):
    pass

# Constants class for storing URLs
class Contanst:
    BASE_URL = "https://www.instagram.com/"
    API_URL = "https://www.instagram.com/api/v1/"

# Class for handling network requests to Instagram
class IGNetWork:
    def __init__(self, proxy: Optional[Dict[str, str]] = None):
        self._proxy = proxy
        self._session = requests.sessions.Session()
        # Set up default headers for requests
        self._session.headers.update({
            'authority': 'www.instagram.com',
            'content-type': 'application/x-www-form-urlencoded',
            'accept': '*/*',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
            'x-ig-app-id': '936619743392459',
            'origin': 'https://www.instagram.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.instagram.com/',
            'accept-language': 'en-US,en;q=0.9,fa-IR;q=0.8,fa;q=0.7'
        })
        # Initial request to set cookies
        self._session.get("https://www.instagram.com/")

    # Property to get CSRF token from cookies
    @property
    def __csrf_token(self):
        cookies = self._session.cookies.get_dict()
        if 'csrftoken' not in cookies:
            raise IGException("CSRF token not found in cookies")
        return cookies['csrftoken']
    
    # Method to make requests with CSRF token
    def __call__(self, url: str, method: str = "GET", **kwargs):
        response = self._session.request(
            url=url,
            method=method,
            proxies=self._proxy,
            headers={
                'x-csrftoken': self.__csrf_token
            },
            **kwargs
        )
        if response.status_code != 200:
            raise IGNetWorkException(f"Failed to request {url} with status code {response.status_code}")
        return response

# Class for handling Instagram Reels
class Reels:
    def __init__(self, user_id: str, page_size: int = 30, max_id: Optional[str] = None, proxy: Optional[Dict[str, str]] = None):
        self.user_id = user_id
        self.page_size = page_size
        self.max_id = max_id
        self._more_available = True
        self._next_max_id = None
        self._network = IGNetWork(proxy=proxy)

    # Method to get reel tray data
    def __get_reel_tray(self):
        url = f"{Contanst.API_URL}clips/user/"
        payload = {
            'target_user_id': self.user_id,
            'page_size': self.page_size,
            'max_id': self.max_id,
            'include_feed_video': True
        }

        response = self._network(url, method="POST", data=payload)
        return response.json()
    
    # Method to parse reel tray data
    def __parse_reel_tray(self, data: dict):
        if data['status'] != 'ok':
            raise IGException("Error while parsing reel tray")

        if data['paging_info']['more_available'] is False:
            self._more_available = False
        else:
            self._next_max_id = data['paging_info']['max_id']

        return data['items']
    
    # Method to get reels
    def get_reels(self):
        data = self.__get_reel_tray()
        return self.__parse_reel_tray(data)
    
    # Method to get next page of reels
    def get_next_reels(self):
        if self._more_available is False:
            return []
        
        self.max_id = self._next_max_id
        return self.get_reels()
    
    # Method to get all reels with optional filters
    def get_all_reels(self, filter_funcs: Optional[List[Callable[[List[Dict]], List[Dict]]]] = None) -> Generator[Dict, None, None]:
        while (reels := self.get_next_reels()):
            if filter_funcs is not None:
                for filter_func in filter_funcs:
                    reels = filter_func(reels)
            yield from reels


        

class ReelsScraper:
    def __init__(self, userid: str, limit: int = 20, min_likes: int = 0, min_views: int = 0):
        self.userid = userid
        self.limit = limit
        self.min_likes = min_likes
        self.min_views = min_views

    def scrape_reels(self):
        reels = []
        reels_obj = Reels(self.userid, page_size=30)
        for reel in reels_obj.get_all_reels(filter_funcs=[
            lambda reels: self.filter_like_count(reels),
            lambda reels: self.filter_views(reels)
        ]):
            reels.append(reel)
            if len(reels) >= self.limit:
                break
        return reels
    
    def filter_like_count(self, reels: List[dict]):
        return [reel for reel in reels if reel['media']['like_count'] >= self.min_likes]

    def filter_views(self, reels: List[dict]):
        return [reel for reel in reels if reel['media']['play_count'] >= self.min_views]

    

    def save_reels_to_json(self, reels: List[dict], output_file: str):
        with open(output_file, 'w') as f:
            json.dump(reels, f, indent=4)
            

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Instagram Reels Scraper")
    parser.add_argument("--userid", type=str, required=True, help="Instagram user id to scrape reels from")
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of reels to fetch (default: 20)")
    parser.add_argument("--min-likes", type=int, default=0, help="Minimum number of likes for a reel to be included (default: 0)")
    parser.add_argument("--min-views", type=int, default=0, help="Minimum number of views for a reel to be included (default: 0)")
    args = parser.parse_args()

    scraper = ReelsScraper(args.userid, args.limit, args.min_likes, args.min_views)
    reels = scraper.scrape_reels()
    scraper.save_reels_to_json(reels, f"{args.userid}_reels.json")



# python reels.py --userid 31051275986 --limit 50 --min-likes 1000 --min-views 10000