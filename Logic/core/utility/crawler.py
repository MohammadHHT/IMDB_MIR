from requests import get
from bs4 import BeautifulSoup
from collections import deque
from concurrent.futures import ThreadPoolExecutor, wait
from threading import Lock
import json
import re


class IMDbCrawler:
    """
    put your own user agent in the headers
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    top_250_URL = 'https://www.imdb.com/chart/top/'

    def __init__(self, crawling_threshold=1000):
        """
        Initialize the crawler

        Parameters
        ----------
        crawling_threshold: int
            The number of pages to crawl
        """
        #* DONE
        self.crawling_threshold = crawling_threshold
        self.not_crawled = deque()
        self.crawled = list()
        self.added_ids = set()
        self.lock = Lock()
        self.add_queue_lock = None

    def get_id_from_URL(self, URL):
        """
        Get the id from the URL of the site. The id is what comes exactly after title.
        for example the id for the movie https://www.imdb.com/title/tt0111161/?ref_=chttp_t_1 is tt0111161.

        Parameters
        ----------
        URL: str
            The URL of the site
        Returns
        ----------
        str
            The id of the site
        """
        #* DONE
        return URL.split('/')[4]

    def write_to_file_as_json(self):
        """
        Save the crawled files into json
        """
        #* DONE
        with open('data/IMDB_crawled.json', 'w') as f:
            json.dump(self.crawled, f)

        with open('IMDB_not_crawled.json', 'w') as f:
            json.dump(self.not_crawled, f)
    def read_from_file_as_json(self):
        """
        Read the crawled files from json
        """
        #* DONE
        with open('data/IMDB_crawled.json', 'r') as f:
            self.crawled = json.load(f)


        self.added_ids = {self.get_id_from_URL(url) for url in self.not_crawled}
        self.added_ids.update([movie['id'] for movie in self.crawled])

    def crawl(self, URL):
        """
        Make a get request to the URL and return the response

        Parameters
        ----------
        URL: str
            The URL of the site
        Returns
        ----------
        requests.models.Response
            The response of the get request
        """
        #* DONE
        response = get(url=URL, headers=self.headers)
        return response

    def extract_top_250(self):
        """
        Extract the top 250 movies from the top 250 page and use them as seed for the crawler to start crawling.
        """
        #* DONE
        response = get(self.top_250_URL, headers=self.headers)
        res = re.search(r'json">([^<]+)</script>', response.text)
        urls = [element['item']['url'] for element in json.loads(res.group(1))['itemListElement']]
        self.not_crawled.extend(urls)
        self.added_ids.update({self.get_id_from_URL(url) for url in urls})


    def get_imdb_instance(self):
        return {
            'id': None,  # str
            'title': None,  # str
            'first_page_summary': None,  # str
            'release_year': None,  # str
            'mpaa': None,  # str
            'budget': None,  # str
            'gross_worldwide': None,  # str
            'rating': None,  # str
            'directors': None,  # List[str]
            'writers': None,  # List[str]
            'stars': None,  # List[str]
            'related_links': None,  # List[str]
            'genres': None,  # List[str]
            'languages': None,  # List[str]
            'countries_of_origin': None,  # List[str]
            'summaries': None,  # List[str]
            'synopsis': None,  # List[str]
            'reviews': None,  # List[List[str]]
        }

    def start_crawling(self):
        """
        Start crawling the movies until the crawling threshold is reached.
        #* DONE
            replace WHILE_LOOP_CONSTRAINTS with the proper constraints for the while loop.
            replace NEW_URL with the new URL to crawl.
            replace THERE_IS_NOTHING_TO_CRAWL with the condition to check if there is nothing to crawl.
            delete help variables.

        ThreadPoolExecutor is used to make the crawler faster by using multiple threads to crawl the pages.
        You are free to use it or not. If used, not to forget safe access to the shared resources.
        """

        # help variables
        # WHILE_LOOP_CONSTRAINTS = None
        # NEW_URL = None
        # THERE_IS_NOTHING_TO_CRAWL = None
        
        self.extract_top_250()
        futures = []
        crawled_counter = 0

        with ThreadPoolExecutor(max_workers=20) as executor:
            while crawled_counter <= self.crawling_threshold:
                crawled_counter += 1
                if self.not_crawled:
                    URL = self.not_crawled.popleft()
                    futures.append(executor.submit(self.crawl_page_info, URL))
                else:
                    wait(futures)
                    break
                    # futures = []

    def crawl_page_info(self, URL):
        """
        Main Logic of the crawler. It crawls the page and extracts the information of the movie.
        Use related links of a movie to crawl more movies.
        
        Parameters
        ----------
        URL: str
            The URL of the site
        """
        # print("new iteration")
        #* DONE?
        response = self.crawl(URL)
        movie = self.get_imdb_instance()
        movie['id'] = self.get_id_from_URL(URL)
        self.extract_movie_info(response, movie, URL)
        with self.lock:
            try:
                new_links = [url for url in movie['related_links'] if self.get_id_from_URL(url) not in self.added_ids]
                self.crawled.append(movie)
                self.not_crawled.extend(new_links)
                self.added_ids.update({self.get_id_from_URL(url) for url in new_links})
            except Exception as e:
                print(e)


    def extract_movie_info(self, res, movie, URL):
        """
        Extract the information of the movie from the response and save it in the movie instance.

        Parameters
        ----------
        res: requests.models.Response
            The response of the get request
        movie: dict
            The instance of the movie
        URL: str
            The URL of the site
        """
        #* DONE
        soup = BeautifulSoup(res.text, features="html.parser")
        data = json.loads(soup.find('script', attrs={'type':'application/ld+json'}).text)
        #*___________________________________
        movie['first_page_summary'] = IMDbCrawler.get_first_page_summary(data)
        movie['title'] = IMDbCrawler.get_title(data)
        movie['directors'] = IMDbCrawler.get_directors(data)
        movie['genres'] = IMDbCrawler.get_genres(data)
        movie['rating'] = IMDbCrawler.get_rating(data)
        movie['writers'] = IMDbCrawler.get_writers(data)
        movie['stars'] = IMDbCrawler.get_stars(data)
        movie['mpaa'] = IMDbCrawler.get_mpaa(data)

        movie['release_year'] = IMDbCrawler.get_release_year(soup)
        movie['budget'] = IMDbCrawler.get_budget(soup)
        movie['gross_worldwide'] = IMDbCrawler.get_gross_worldwide(soup)
        movie['related_links'] = IMDbCrawler.get_related_links(soup)
        movie['languages'] = IMDbCrawler.get_languages(soup)
        movie['countries_of_origin'] = IMDbCrawler.get_countries_of_origin(soup)
        #*___________________________________
        summery = BeautifulSoup(self.crawl(IMDbCrawler.get_summary_link(URL)).text, features="html.parser")
        movie['summaries'] = IMDbCrawler.get_summaries(summery)
        movie['synopsis'] = IMDbCrawler.get_synopsis(summery)
        #*___________________________________
        review = BeautifulSoup(self.crawl(IMDbCrawler.get_review_link(URL)).text, features="html.parser")
        movie['reviews'] = IMDbCrawler.get_reviews_with_scores(review)


    def get_summary_link(url):
        """
        Get the link to the summary page of the movie
        Example:
        https://www.imdb.com/title/tt0111161/ is the page
        https://www.imdb.com/title/tt0111161/plotsummary is the summary page

        Parameters
        ----------
        url: str
            The URL of the site
        Returns
        ----------
        str
            The URL of the summary page
        """
        try:
            #* DONE
            return url + 'plotsummary/'
        except:
            print("failed to get summary link")

    def get_review_link(url):
        """
        Get the link to the review page of the movie
        Example:
        https://www.imdb.com/title/tt0111161/ is the page
        https://www.imdb.com/title/tt0111161/reviews is the review page
        """
        try:
            #* DONE
            return url + 'reviews/'
        except:
            print("failed to get review link")

    def get_title(data):
        """
        Get the title of the movie from the soup

        Parameters
        ----------
        data: dict
            The json data in page
        Returns
        ----------
        str
            The title of the movie

        """
        try:
            #* DONE
            return data['name']
        except:
            print(f"{data['name']}-failed to get title")

    def get_first_page_summary(data):
        """
        Get the first page summary of the movie from the soup

        Parameters
        ----------
        data: dict
            The json data in page
        Returns
        ----------
        str
            The first page summary of the movie
        """
        try:
            #* DONE
            return data['description']
                
        except:
            print(f"{data['name']}-failed to get first page summary")

    def get_directors(data):
        """
        Get the directors of the movie from the soup

        Parameters
        ----------
        data: dict
            The json data in page
        Returns
        ----------
        List[str]
            The directors of the movie
        """
        try:
            #* DONE
            return [director['name'] for director in data['director']]
        except:
            print(f"{data['name']}-failed to get director")

    def get_stars(data):
        """
        Get the stars of the movie from the soup

        Parameters
        ----------
        data: dict
            The json data in page
        Returns
        ----------
        List[str]
            The stars of the movie
        """
        try:
            #* DONE
            return [actor['name'] for actor in data['actor']]
        except:
            print(f"{data['name']}-failed to get stars")

    def get_writers(data):
        """
        Get the writers of the movie from the soup

        Parameters
        ----------
        data: dict
            The json data in page
        Returns
        ----------
        List[str]
            The writers of the movie
        """
        try:
            #* DONE
            return [creator['name'] for creator in data['creator'] if 'name' in creator.keys()] 
        except:
            print(f"{data['name']}-failed to get writers")

    def get_related_links(soup):
        """
        Get the related links of the movie from the More like this section of the page from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[str]
            The related links of the movie
        """
        try:
            #* DONE
            return ['https://www.imdb.com' + tag['href'] for tag in soup('a') if re.match(r'/title/([^/]+)/\?ref_=tt_sim.+', tag['href']) and tag.text.strip()]
        except:
            print(f"{soup.title.text}-failed to get related links")

    def get_summaries(soup):
        """
        Get the summary of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[str]
            The summary of the movie
        """
        try:
            #* DONE
            summeries = soup.find('span', attrs={'id':'summaries'})
            sec = summeries.findParent('section')
            return [' '.join(li.text.split()) for li in sec.ul('li')]
            
        except:
            print(f"{soup.title.text}-failed to get summary")

    def get_synopsis(soup):
        """
        Get the synopsis of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[str]
            The synopsis of the movie
        """
        try:
            #* DONE
            synopsis = soup.find('span', attrs={'id':'synopsis'})
            sec = synopsis.findParent('section')
            return [' '.join(li.text.split()) for li in sec.ul('li')]
        except:
            print(f"{soup.title.text}-failed to get synopsis")

    def get_reviews_with_scores(soup):
        """
        Get the reviews of the movie from the soup
        reviews structure: [[review,score]]

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[List[str]]
            The reviews of the movie
        """
        try:
            #* DONE
            reviews = list()
            for tag in soup('div', attrs={'class':'lister-item-content'}):
                if span := tag.find('span', attrs={'class':"rating-other-user-rating"}):
                    rating = ' '.join(span.text.split())
                else:
                    rating = '-'
                title = tag.find('a', attrs={'class':"title"}).text.strip()
                text = tag.find('div', attrs={'class':'text show-more__control'}).text
                text = '\n'.join(re.split('[\s]{2,}', text))
                reviews.append(['\n'.join([title,text]), rating])
            return reviews
        except:
            print(f"{soup.title.text}-failed to get reviews")

    def get_genres(data):
        """
        Get the genres of the movie from the soup

        Parameters
        ----------
        data: dict
            The json data in page
        Returns
        ----------
        List[str]
            The genres of the movie
        """
        try:
            #* DONE
            return data['genre']
        except:
            print("Failed to get generes")

    def get_rating(data):
        """
        Get the rating of the movie from the soup

        Parameters
        ----------
        data: dict
            The json data in page
        Returns
        ----------
        str
            The rating of the movie
        """
        try:
            #* DONE
            return data['aggregateRating']['ratingValue']
        except:
            print(f"{data['name']}-failed to get rating")

    def get_mpaa(data):
        """
        Get the MPAA of the movie from the soup

        Parameters
        ----------
        data: dict
            The json data in page
        Returns
        ----------
        str
            The MPAA of the movie
        """
        try:
            #* DONE
            return data['contentRating']
        except:
            print(f"{data['name']}-failed to get mpaa")

    def get_release_year(soup):
        """
        Get the release year of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        str
            The release year of the movie
        """
        try:
            #* DONE
            tag = soup.find('li', attrs={'data-testid':"title-details-releasedate"})
            return tag.ul.text.strip()
        except:
            print(f"{soup.title.text}-failed to get release year")

    def get_languages(soup):
        """
        Get the languages of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[str]
            The languages of the movie
        """
        try:
            #* DONE
            tag = soup.find('li', attrs={'data-testid':"title-details-languages"})
            return re.split('[\s]{2,}', tag.ul.text.strip())
        except:
            print(f"{soup.title.text}-failed to get languages")
            return None

    def get_countries_of_origin(soup):
        """
        Get the countries of origin of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[str]
            The countries of origin of the movie
        """
        try:
            #* DONE
            tag = soup.find('li', attrs={'data-testid':"title-details-origin"})
            return re.split('[\s]{2,}', tag.ul.text.strip())
        except:
            print(f"{soup.title.text}-failed to get countries of origin")

    def get_budget(soup):
        """
        Get the budget of the movie from box office section of the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        str
            The budget of the movie
        """
        try:
            #* DONE
            tag = soup.find('li', attrs={'data-testid':"title-boxoffice-budget"})
            return tag.li.text.strip()
        except:
            print(f"{soup.title.text}-failed to get budget")

    def get_gross_worldwide(soup):
        """
        Get the gross worldwide of the movie from box office section of the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        str
            The gross worldwide of the movie
        """
        try:
            #* DONE
            tag = soup.find('li', attrs={'data-testid':"title-boxoffice-cumulativeworldwidegross"})
            return tag.li.text.strip()
        except:
            print(f"{soup.title.text}-failed to get gross worldwide")


def main():
    imdb_crawler = IMDbCrawler(crawling_threshold=600)
    # imdb_crawler.read_from_file_as_json()
    imdb_crawler.start_crawling()
    imdb_crawler.write_to_file_as_json()


if __name__ == '__main__':
    main()
