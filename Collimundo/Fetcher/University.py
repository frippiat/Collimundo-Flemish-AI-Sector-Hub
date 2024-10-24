import requests
from bs4 import BeautifulSoup
from collimundo_database import GremlinGraphManager
from KBO_AI import KBO_AI
import json
from urllib.parse import urlparse
from scraper import Company_Scraper
from Company_Page_Fetcher import external_company_fetcher
import datetime

class University:
    def __init__(self, university='Ghent University'):
        self.university = university
        self.ghent = Ghent('https://www.ugent.be/voor-organisaties-en-bedrijven/en/techtransfer/overview.htm')
        self.leuven = Leuven('https://lrd.kuleuven.be/spinoff/spinoff-bedrijven')
        self.antwerp = Antwerp('https://www.uantwerpen.be/nl/onderzoek/informatie-voor-bedrijven/spin-offs-uantwerpen/overzicht-spin-offs/')
        self.vub = VUB('https://www.vubtechtransfer.be/spin-off-portfolio-0?sort_by=title&sort_order=DESC&page=0')
        self.ai = KBO_AI()
        self.cosmos = GremlinGraphManager()
        self.company_scraper = Company_Scraper(forbidden= ["videos","images","industrial", "academy", "distributors", "article", "articles", "newsletters", "newsletter", "data-privacy-notice", "legal-terms", "legal-terms", "legality", "cookies", "cookie-statement", "certifications", "webinar", "webinars", "news_events", "tagged", "privacy-policy", "news", "insights", "nieuws", "blog", "podcast", "podcasts", "events", "event", "career", "careers", "jobs", "job", "privacy", "policies" ,"policy","pdf"],
                 languages = ["fr", "ko", "cs", "ro", "it", "ja", "nl", "es", "de", "dk", "se", "fi", "no", "pl", "ar", "bg", "zh", "hr", "da", "el", "he", "hi", "hu", "id", "lt", "mn", "pt", "ru", "sk", "sr", "sv", "th", "tr", "vi"],debug=True)
        self.external = external_company_fetcher()

    def university_structure(self):  
        unief_implementors = []
        if self.university == 'Ghent University':
            unief_implementors = self.ghent.get_text()
        elif self.university == 'KU Leuven':
            unief_implementors = self.leuven.get_text()
        elif self.university == 'University of Antwerp':
            unief_implementors = self.antwerp.get_text()
        elif self.university == 'Vrije Universiteit Brussel':
            unief_implementors = self.vub.get_text()
        
        for element in unief_implementors:
            if (self.ai.check_companies(element) ==1):
                print(f"{element} is AI company")
                try:
                    data = {}
                    website = self.company_scraper.get_scraper().get_url_from_name(element)

                    data['website'] = website
                    #if already available:
                    if self.cosmos.is_vertex_in_graph({'id' : urlparse(website).netloc}):
                        continue

                    #easy to extract information
                    data['id'] = urlparse(website).netloc
                    data['actor'] = "implementor"
                    data['name'] = element
                    data['name_lower'] = element.lower()
                    try:
                        data['photo'] = self.company_scraper.get_company_logo(element)
                    except:
                        data['photo']=''
                        print("something wrong with the logo fetcher")
                    

                    print(f"time to generate the company page using openai: ")
                    scraped_info = self.company_scraper.generate_company_pages([element])
                    if len(scraped_info) != 6:
                        scraped_info = scraped_info[0]
                        print(f"retrieved scraped data: {scraped_info}")
                    
                    data['description'] = scraped_info[1]
                    
                    #social media:
                    for social in scraped_info[2]:
                        if 'facebook' in social.lower():
                            data['facebook'] = social
                        elif 'linkedin' in social.lower():
                            data['linkedin'] = social
                        elif 'instagram' in social.lower():
                            data['instagram'] = social
                        else:
                            data['twitter'] = social
                    
                    #telephone + email:
                    for contact in scraped_info[3]:
                        if '@' in contact:
                            data['email'] = contact
                        else:
                            data['tel'] = contact
                    
                    #keypartners and domain tag links:
                    data['links'] = {'works_on' : [], 'external_partner' : [], 'uni_partner':[self.university],'uni_alumni':[self.university]}
                    for keypartner in scraped_info[4]:
                        if keypartner != '':
                            # key for database -> netwerklocatie
                            website = self.company_scraper.scraper.get_url_from_name(keypartner)
                            if website !=None:
                                database_id = urlparse(website).netloc
                            else:
                                database_id = keypartner
                                website = keypartner
                            if not isinstance(database_id, str):
                                continue
                            #check if already available:
                            if not self.cosmos.is_vertex_in_graph({'id' : database_id}):
                                print("niet aanwezig")
                                self.external.create_json(keypartner, website)
                                print(f"external partner added: {database_id}")
                            else:
                                print("av")
                                print(f"external partner already present: {database_id}")
                            if str(database_id) != 'www.companyweb.be' or str(database_id) != 'www.belgium.be':
                                data['links']['external_partner'].append(str(database_id))

                    print(f"works on: {scraped_info[5]}")
                    for tag in scraped_info[5]:
                        data['links']['works_on'].append('domain_' + tag)
                    print(f"final data: {data}")
                    file_path = "./data/" + element + ".json"
                    print(f"file path: {file_path}")
                    with open(file_path, 'w') as json_file:
                        print(f"json file created for {element}")
                        json.dump(data, json_file, indent=4)
                        print(f"json file created for {element}")
                    self.cosmos.write_to_graph()
                    print(f"company added to graph: {element}")
                except:
                    print("something went wrong with the data retrieval")

            else:
                print(f"{element} is not AI company")

class Ghent:
    def __init__(self,url):
        self.url = url


    def get_text(self):

        html = requests.get(self.url).text

        # Find all <a> tags within <td> tags
        soup = BeautifulSoup(html, 'html.parser')
        company_tags = soup.find_all('td')

        # Extract company names from <a> tags
        companies = [tag.find('a').text.strip() for tag in company_tags if tag.find('a')]
        companies = [name.strip(':') for name in companies][10:]
        
        return companies 
    

class Leuven:
    def __init__(self,url):
        self.url = url

    def get_text(self):

        html = requests.get(self.url).text
        soup = BeautifulSoup(html, 'html.parser')
        company_tags = soup.find_all('p')

        # Extract company names from <a> tags
        companies = [tag.find('a').text.strip() for tag in company_tags if tag.find('a')][2:-1]
        companies = [name for name in companies if name != '']
        
        return companies
    
class Antwerp:
    def __init__(self,url):
        self.url = url

    def get_text(self):

        html = requests.get(self.url).text
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find all <h2> tags within <summary> tags
        company_tags = soup.find_all('summary')

        # Extract company names from <h2> tags
        companies = [tag.text.strip() for tag in company_tags]
        companies = [name.split(" (")[0] for name in companies]
        

        return companies

class VUB:
    def __init__(self,url):
        self.url = url

    def get_text(self):

        companies_final = []
        page = 0
        possible = True
        while possible:
            html = requests.get(self.url).text
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find all <h3> tags within <div> tags
            company_tags = soup.find_all('h3')

            # Extract company names from <h3> tags
            companies = [tag.text.strip() for tag in company_tags]
            companies = [name.split(" (")[0] for name in companies]
            if companies == []:
                possible = False
            companies_final += companies
            page+=1
            self.url = self.url[:-1] + str(page)
        
        return companies_final

if __name__ == "__main__":
    university_test_ghent = University('Ghent University')
    university_test_ghent.university_structure()

