
from scraper import scraper
import requests 
from bs4 import BeautifulSoup
from AzureCommunication import AzureOpenAICommunication
import ast
from urllib.parse import urlparse
from collimundo_database import GremlinGraphManager
import json
import re
import time


class Portfolio:
    def __init__(self,root):
        self.root=root
        self.Scrapen = scraper(forbidden= ["team","industrial", "academy", "distributors", "article", "articles", "newsletters", "newsletter", "data-privacy-notice", "legal-terms", "legal-terms", "legality", "cookies", "cookie-statement", "certifications", "webinar", "webinars", "news_events", "tagged", "privacy-policy", "news", "insights", "nieuws", "blog", "podcast", "podcasts", "events", "event", "career", "careers", "jobs", "job", "privacy", "policies" ,"policy","pdf"],
                 languages = ["fr", "ko", "cs", "ro", "it", "ja", "es", "de", "dk", "se", "fi", "no", "pl", "ar", "bg", "zh", "hr", "da", "el", "he", "hi", "hu", "id", "lt", "mn", "pt", "ru", "sk", "sr", "sv", "th", "tr", "vi"])
        self.openAI = AzureOpenAICommunication()
        self.db = GremlinGraphManager()

    def get_urls(self):

        try:
            url = f"https://www.vlaio.be/nl/begeleiding-advies/financiering/risicokapitaal/zoek?page=100"
            response = requests.get(url)
        except:
            return 0
        
        soup = BeautifulSoup(response.content, 'html.parser')
        investors = [a.get('aria-label') for a in soup.find_all('a', href=True) if a.get('aria-label')][3:]

        return investors

    def get_investor(self, name):
        name_url = name.replace('&', '-').lower()
        name_url = name_url.replace('@', '').lower()
        name_url = name_url.replace('(', '').lower()
        name_url = name_url.replace('.', '').lower()
        name_url = name_url.replace(')', '').lower()
        name_url = name_url.replace('+', '').lower()
        name_url = name_url.replace('é', 'e').lower()
        name_url = name_url.replace(' - ', '-').lower()
        name_url = name_url.replace(' ', '-').lower()
        url = f"https://www.vlaio.be/nl/begeleiding-advies/financiering/risicokapitaal/{name_url}"

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes
            soup = BeautifulSoup(response.content, 'html.parser')

            summary = soup.find('div', class_='field--field-tekst').p.text.strip() if soup.find('div', class_='field--field-tekst') else ''
            summary = re.sub(r'[^\w\s]', '', summary)
            zipcode = soup.find('span', class_='postal-code').text.strip() if soup.find('span', class_='postal-code') else ''
            email = soup.find('div', class_='field--field-email').text[14:-1].strip() if soup.find('div', class_='field--field-email') else ''
            phone = soup.find('div', class_='field--field-telefoon').text[11:-1].strip() if soup.find('div', class_='field--field-telefoon') else ''
            website = soup.find('div', class_='field--field-website').text[10:-1].strip() if soup.find('div', class_='field--field-website') else ''
            city = soup.find('span', class_='locality').text.strip() if soup.find('span', class_='locality') else ''
            investment_scope = soup.find("ul").text.strip() if soup.find("ul") else ''
            street = ''
            house_number = ''
            try:
                street = soup.find('span', class_='address-line1').text.strip()
                parts = street.split(" ")
                for part in parts:
                    if part.isdigit():
                        house_number = part
                    else:
                        street += " " + part
            except:
                None
            if 'Groeifinanciering' in investment_scope:
                investment_scope = 'accelerator'
            else:
                investment_scope = 'venture capital'
            try:
                logo = self.Scrapen.get_company_logo(name)
            except:
                logo=''
                print("something wrong with the logo fetcher")
                
            investor = {
                "name": name,
                "id": name,
                "name_lower": name.lower(),
                "actor": "investor",
                "summary": summary,
                "logo": logo,
                "city": city,
                "zipcode": zipcode,
                "street": street,
                "housenumber": house_number,
                "email": email,
                "phone": phone,
                "website": website,
                "city": city,
                "investment scope": investment_scope,
                "links": {
                    "invests_in": []
                }
            }
            return investor
        
        except requests.RequestException as e:
            print(f"Error fetching data for {name}: {e}")
            return None
        
    def search_portfolio(self,root):
        """
        Searches for the page where the invested companies are listed.

        Inputs:
        - root: The root URL of the investor site

        Returns:
        - The URL of the page where the invested companies are listed
        """
        todo = [root]  # array with all not yet visited pages
        done = []  # already visited pages, we do not want infinite loops

        while (len(todo) > 0):  # as long as we did not yet visit all pages
            # debugging:
            print(f"next iteration : {todo[0]}")
            print(f"to do = {len(todo)}")
            print(f"already done = {len(done)}")

            curr_url = todo.pop(0)

            if curr_url:
                done.append(curr_url)
                # add to do if not already done
                try:
                    subpages = self.Scrapen.get_urls_from_seed(root, curr_url)
                    for subpage in subpages:
                        if subpage not in done and subpage not in todo:
                            #check if its not the url we are searching for:

                            todo.append(subpage)
                except:
                    return ['']


        # Get all URLs from the root
        try:
            urls = self.Scrapen.get_urls_from_seed(root, root)
        except:
            pass
        # Search for portfolio-related keywords in the URLs
        portfolio_keywords = ["#portfolio","portfolio", "portefeuille", "investeringen", "invested", "participaties"] # add if you found other keywords that work
        portfolio_url = None

        for url in urls:
            for keyword in portfolio_keywords:
                if keyword in url.lower():
                    portfolio_url = url
                    break
            if portfolio_url:
                break

        return portfolio_url


    def invest_list(self,portfolio_url):
        """
        Extracts the text of the HTML and returns a list of company names.

        Inputs:
        - portfolio_url: The URL of the page where the invested companies are listed

        Returns:
        - A list of company names
        """
        # Get text content from the portfolio URL
        text_content = self.Scrapen.get_text_from_url(portfolio_url)
        if not text_content:
            print("Failed to retrieve text content from the provided URL.")
            return None

        # Split text content into lines and extract company names
        lines = text_content.split('\n')
        company_names = []
        for line in lines:
            # Add conditions to filter out irrelevant text and extract company names
            # Example: extract company names if they follow certain patterns in the text
            if line:  # Check if line is not empty
                company_names.append(line.strip())  # Add company name to the list after stripping whitespace

        return company_names
    
    def retrieve_companies(self,lst):
        ans = []
        openai_companies = self.openAI.communicate("Your task is to analyze a text of a company portfolio website and to return only the names of the companies listed on the portfolio that this company invests in. "
                                                        "Please return a list of company names"
                                                        "If there are no companies, only return [''], with no other explanation! ", str(lst))

        ans.extend(ast.literal_eval(openai_companies))
        print("Companies from OpenAI: ")
        print(ans)
        companies=[]
        for company in ans:
            id = urlparse(portfolio.Scrapen.get_url_from_name(str(company))).netloc
            if id!=b'':
                if self.db.is_vertex_in_graph({'id' : id}):
                    companies.append(id)
        return companies
    
    def update_investors(self):
        for investor in self.get_urls():
            try:
                print("Investor: ", investor, "\n")
                url = self.Scrapen.get_url_from_name(investor)
                if url ==None:
                    url = "https://"+self.get_investor(investor)["website"]
                print("URL: ", url, "\n")
                self.root=url
                lst = portfolio.invest_list(url)
                companies = portfolio.retrieve_companies(lst)
                investor_json = self.get_investor(investor)
                companies = [name for name in companies if name !='www.belgium.be']
                investor_json["links"]["invests_in"] = companies
                print(investor_json)
                with open(f"./data/{investor}.json", "w") as json_file:
                    json.dump(investor_json, json_file, indent=4,ensure_ascii=False)
                if len(companies) > 0:
                    time.sleep(2)
                    self.db.write_to_graph()
            except:
                print("Something went wrong with the data retrieval")

        return 1
    
if __name__ == "__main__":
    portfolio = Portfolio('https://www.gimv.com')
    portfolio.update_investors()

