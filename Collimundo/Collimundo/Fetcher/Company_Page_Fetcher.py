from scraper import Company_Scraper
import datetime
from keystructure import keymaster
from Financial_information import Financial_source
from urllib.parse import urlparse
try:
    from ..search_engine.GremlinGraphManager import GremlinGraphManager
except:
    from .GremlinGraphManager import GremlinGraphManager
import json

# the fetcher to create company pages/where you can ask information -> can ask for updates of
class external_company_fetcher:
    def __init__(self):
        self.company_scraper = Company_Scraper()

    def create_json(self, name,  website=None):
        if not website:
            website = self.company_scraper.get_scraper().get_url_from_name(name)

        data = {}
        data['name'] = name
        data['id'] = urlparse(website).netloc
        data['actor'] = 'external'
        data['website'] = website
        try:
            data['photo'] = self.company_scraper.get_company_logo(name)
        except:
            data['photo'] = ""
        #save it
        file_path = "./data/" + name + ".json"

        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
            json_file.flush()  # Flush data to disk


class fetcher():
    def __init__(self, debug=False):
        #to keep track of the needed update file of kbo
        current_date = datetime.date.today()
        self.kbo_nr = 116 #todo: can this be also done automatically??
        self.year = current_date.year
        self.month = current_date.month

        # Keymaster to make the usage of keys very modefiable
        self.keymaster = keymaster()

        #printing?
        self.debug = debug

        # data sources
        self.company_scraper = Company_Scraper(debug=self.debug)
        self.financial = Financial_source()
        self.cosmos = GremlinGraphManager() #internal data
        self.external = external_company_fetcher()

        #self.KBO
        #todo: structure of vincents code

        #to get the fails
        self.fails = ["biolizard"]

    #when deleted, make sure to store its fails
    def __del__(self):
        if self.fails:
            with open("fetcher_logbook/" + datetime.date.today().year + datetime.date.today().month
                      + datetime.date.today().day + ".txt", 'w') as file:
                file.write(str(self.fails))

    # ask to update any information of already present todo
    def update(self, type, name):
        assert "not yet implemented! the company pages have priority!"

    def KBO_update(self):
        """Every month, a KBO update file should be checked automatically for possible new implementors"""
        # Get current date
        current_date = datetime.date.today()
        #if current_date.month < self.month or current_date.year < self.year:
        #    return None #no updates possible

        #step 1: Get the url to download the new update file
        KBO_file = "https://kbopub.economie.fgov.be/kbo-open-data/affiliation/xml/files/KboOpenData_" + \
                   str((4-len(str(self.kbo_nr)))*'0') + str(self.kbo_nr) + \
                    "_" + str(self.year) + "_" + str(self.month) + "_Update.zip"

        #step 2: KBO source -> list of information of companies identified as implementors
        #todo: need a structure from vincent that just returns a list of dict with name and vat + when does these fail?
        implementors = [
            {'vat': '0835731610', 'name': 'flir'},
            {'vat': '0454064819', 'name': 'gim'},
            {'vat': '0866039556', 'name': 'hict'},
            {'vat': '0478890483', 'name': 'hydroscan'},
            {'vat': '0444177945', 'name': 'ocas'},
            {'vat': '0473191041', 'name': 'barco'},
            {'vat': '0467667088', 'name': 'boplan'},
            {'vat': '0405502362', 'name': 'picanol'}
            #{'vat': '0563644135', 'name': 'hello customer'},
            #{'vat': '0803978263', 'name': 'legalfly'},
            #{'vat': '0702877935', 'name': 'novable'},
            #{'vat': '0478493179', 'name': 'ixor'},
            #{'vat': '0794564414', 'name': 'jelloow'},
            #{'vat': '0745522501', 'name': 'nannyml'},
            #{'vat': '0537905085', 'name': 'iretailcheck'},
            #{'vat': '0818030890', 'name': 'foodpairing'},
            #{'vat': '0720636061', 'name': 'ArtiQ'},
            #{'vat': '0675758517', 'name': 'bingli'},
            #{'vat': '0475477964', 'name': 'vivansa'},
            #{'vat': '0742718508', 'name': 'segments.ai'},
        ]

        #step 3: for every implementor -> use its denomination to scrape the page + get financial information with Staatsbladmonitor
        for element in implementors:
            try:
                data = {}
                website = self.company_scraper.get_scraper().get_url_from_name(element['name'])
                data['website'] = website
                if self.debug:
                    print(f"next: {website}")
                #if already available:
                if self.cosmos.is_vertex_in_graph({'id' : urlparse(website).netloc}):
                    continue

                #easy to extract information
                data['id'] = urlparse(website).netloc
                data['actor'] = "implementor"
                data['name'] = element['name']
                data['name_lower'] = element['name'].lower()
                try:
                    data['photo'] = self.company_scraper.get_company_logo(element['name'])
                except:
                    if self.debug:
                        print("something wrong with the logo fetcher")
                data['vat'] = element['vat']

                #scraped info
                if self.debug:
                    print(f"time to generate the company page using openai: ")
                scraped_info = self.company_scraper.generate_company_pages([element['name']])
                # sometimes openAI gives weird formats .. todo? prompt engineering xd
                if len(scraped_info) != 6:
                    scraped_info = scraped_info[0]
                if self.debug:
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
                data['links'] = {'works_on' : [], 'external_partner' : []}
                for keypartner in scraped_info[4]:

                    # key for database -> netwerklocatie
                    website = self.company_scraper.scraper.get_url_from_name(keypartner)
                    database_id = urlparse(website).netloc
                    if not isinstance(database_id, str):
                        continue
                    #check if already available:
                    if not self.cosmos.is_vertex_in_graph({'id' : database_id}):
                        self.external.create_json(keypartner, website)
                    else:
                        if self.debug:
                            print("av")
                            print(f"external partner already present: {database_id}")

                    data['links']['external_partner'].append(str(database_id))


                for tag in scraped_info[5]:
                    data['links']['works_on'].append('domain_' + tag)
                if self.debug:
                    print("financial information extraction:")
                #financials:
                financial = self.financial.StaadsbladMonitor(element['vat'])
                data['zipcode'] = financial['zipcode']
                data['street'] = financial['street']
                data['housenumber'] = financial['housenumber']
                data['city'] = financial['city']
                data['startdate'] = financial['start date']
                data['financial'] = str(financial['financial'])

                if self.debug:
                    print("---------------------------------------------storing, time for next iteration--------------------------------------")
                #step 4: -> store in file
                file_path = "./data/" + element['name'] + ".json"

                with open(file_path, 'w') as json_file:
                    json.dump(data, json_file, indent=4)

            except Exception as e: #if something fails, no crash is needed, but store in the failed processes that can be retrieved
                if self.debug:
                    print(f"fault!! {element['name']} -> {e}")
                self.fails.append((element['name'], data))

        #make all variables ready for the next time the update file gets called
        self.kbo_nr+=1
        self.year += (self.month==12)
        self.month = (self.month+1)%12


if __name__=="__main__":
    fetcher = fetcher(debug=True)
    fetcher.KBO_update()
