from newspaper import Article
import gdelt
from datetime import datetime, timedelta
import nltk
import warnings
import re
import json
import os
import requests
import xmltodict
warnings.filterwarnings("ignore", category=UserWarning)
nltk.download('punkt', quiet=True)

class NewsArticle:
    def __init__(self):
        pass
    # Get information based on the URL of the news article
    def url_summary(self,url_input):
        """
        Retrieves information from a given URL and returns a dictionary containing the article information.

        Parameters:
        url_input (str): The URL of the article.

        Returns:
        dict: A dictionary containing the following information:
            - Title: The title of the article.
            - Authors: The author(s) of the article.
            - Image: The URL of the main image in the article.
            - Keywords: The keywords associated with the article.
            - Date: The publish date of the article.
            - URL: The input URL.

        """
        url = url_input
        article = Article(url)
        article.download()
        article.parse()

        # Create a dictionary to store information
        article_info = {
            "Title": article.title,
            "Authors": article.authors[0] if article.authors else None,
            "Image": article.top_image,
            "Keywords": article.keywords,
            "Date": article.publish_date,
            "URL": url_input
        }

        return article_info

    # Initialize gdelt API & Filter articles
    def initialize_gdelt(self,filter_input, date_input):
        """
        Initializes the GDELT object and performs a search based on the given filter input and date range.

        Args:
            filter_input (str): The filter input to be used for searching.
            date_input (int): The number of days to go back from the current date.

        Returns:
            pandas.DataFrame: A DataFrame containing the filtered results with columns 'SOURCEURL' and 'Actor1CountryCode'.
        """
        gd = gdelt.gdelt(version=2)
        start_date = (datetime.now() - timedelta(days=date_input)).strftime("%Y%m%d%H%M%S")
        end_date = datetime.now().strftime("%Y%m%d%H%M%S")
        results = gd.Search([start_date, end_date], table='events', coverage=True)
        urls_and_countries = results[['SOURCEURL', 'Actor1CountryCode']].dropna()
        
        # Replace spaces with - in the filter input
        filter_input = filter_input.replace(' ', '-')
        
        keyword_pattern = re.compile(r'\b{}\b'.format(re.escape(filter_input)), re.IGNORECASE)
        filtered_results = urls_and_countries[urls_and_countries['SOURCEURL'].str.contains(keyword_pattern)]
        return filtered_results

    # Return unique articles 
    def filter_articles(self,keyword_input, date_input):
        """
        Filter articles based on a keyword and date.

        Args:
            keyword_input (str): The keyword to filter articles.
            date_input (int): The number of days to filter articles from.

        Returns:
            list: A list of filtered articles.

        """
        filtered_result = self.initialize_gdelt(keyword_input, 2)
        article_list = []

        for url, c in zip(filtered_result['SOURCEURL'], filtered_result['Actor1CountryCode']):
            article = Article(url)

            try:
                entry = self.url_summary(url)
                if entry not in article_list:
                    article_list.append(entry)
            except Exception as e:
                pass
            
        # Filter out articles with missing dates
        articles_with_dates = [article for article in article_list if article.get('Date') is not None]

        # Convert all datetime objects to timezone-naive
        for article in articles_with_dates:
            if article['Date'].tzinfo:
                article['Date'] = article['Date'].replace(tzinfo=None)

        # Sort articles based on the "Date" field in descending order
        sorted_articles = sorted(articles_with_dates, key=lambda x: x.get('Date'), reverse=True)
    
        return sorted_articles

    def json_serial(self,obj):
        """
        Serializes the given object to JSON format.

        Args:
            obj: The object to be serialized.

        Returns:
            The serialized object in JSON format.

        Raises:
            TypeError: If the object is not serializable.
        """
        if isinstance(obj, datetime):
            if obj.tzinfo is not None:
                obj = obj.astimezone(datetime.timezone.utc).replace(tzinfo=None)
            return obj.isoformat()
        raise TypeError("Type not serializable")

    def initialize_vrt(self):
        """
        Fetches news articles from the VRT RSS feed, parses the data, and saves it to a JSON file.

        Returns:
            str: A message indicating that the news data has been saved.
        """
        url = "https://www.vrt.be/vrtnws/en.rss.articles.xml"
        response = requests.get(url)
        data = xmltodict.parse(response.content)

        news_entries = data['feed']['entry']

        # List to store news entries
        news_list = []

        for entry in news_entries:
            title = entry['title']['#text']
            published_date = entry['published']
            url = entry['link'][1]['@href']
            try:
                image = entry['link'][2]['@href']
            except:
                image = ' '
            authors = entry.get('author', {}).get('name', '')
            keywords = entry.get('vrtns:nstag', {}).get('#text', '')
            
            # Create a dictionary for each news entry
            news_entry = {
                'Title': title,
                'Authors': authors,
                'Image': image,
                'Keywords': keywords,
                'Date': published_date,
                'URL': url
            }
            
            # Append the dictionary to the list
            news_list.append(news_entry)

        # Filter out articles with missing dates
        articles_with_dates = [article for article in news_list if article.get('Date') is not None]

        # Sort articles based on the "Date" field in descending order
        sorted_articles = sorted(articles_with_dates, key=lambda x: x.get('Date'), reverse=True)


        # Write the sorted list of dictionaries to a JSON file
        filename = os.path.join(os.path.dirname(__file__), 'data', "vrt.json")
        with open(filename, 'w') as f:
            json.dump(sorted_articles, f, indent=4)

        return "News data has been saved"

    def save_articles(self,keyword, date_input):
        """
        Save articles filtered by keyword and date_input to a JSON file.

        Args:
            keyword (str): The keyword to filter the articles.
            date_input (str): The date input to filter the articles.

        Returns:
            None
        """
        articles = self.filter_articles(keyword, date_input)
        filename = os.path.join(os.path.dirname(__file__), 'data', f"{keyword}.json")
        with open(filename, 'w') as f:
            json.dump(articles, f, indent=4, default=self.json_serial)

    # Example
    # Filter on word, last 2 days & dump to json file & vrt headlines
    def get_newsarticles(self):
        current_time = datetime.now()
        print("Timestamp 1:", current_time)
        self.initialize_vrt()
        current_time = datetime.now()
        print("Timestamp 2:", current_time)
        keywords = ['belgium', 'sustainability', 'AI']
        print("gdelt news articles hourly pull")
        for keyword in keywords:
            current_time = datetime.now()
            print(f"Timestamp {keyword} pre:", current_time)
            self.save_articles(keyword, 2)
            current_time = datetime.now()
            print(f"Timestamp {keyword} post:", current_time)
        
if __name__ == "__main__":
    Newsarticle = NewsArticle()
    Newsarticle.get_newsarticles()
