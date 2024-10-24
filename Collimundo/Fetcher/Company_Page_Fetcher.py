from scraper import Company_Scraper
import datetime
from keystructure import keymaster
from Financial_information import Financial_source
from urllib.parse import urlparse, urljoin
from collimundo_database import GremlinGraphManager
import json
from KBO import KBO
from KBO_AI import KBO_AI

# the fetcher to create company pages/where you can ask information -> can ask for updates of
class external_company_fetcher:
    def __init__(self):
        self.company_scraper = Company_Scraper()

    def create_json(self, name,  website=None):
        if not website:
            website = self.company_scraper.get_scraper().get_url_from_name(name)
        if website != 'https://www.companyweb.be' or website != 'https://www.belgium.be':
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
        else:
            None


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
        self.kbo = KBO()
        self.kbo_ai = KBO_AI()
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

        # #step 1: Get the url to download the new update file
        # KBO_file = "https://kbopub.economie.fgov.be/kbo-open-data/affiliation/xml/files/KboOpenData_" + \
        #            str((4-len(str(self.kbo_nr)))*'0') + str(self.kbo_nr) + \
        #             "_" + str(self.year) + "_" + str(self.month) + "_Update.zip"

        #step 2: KBO source -> list of information of companies identified as implementors
        #todo: need a structure from vincent that just returns a list of dict with name and vat + when does these fail?
        # implementors = [
        #     {'vat': '0835731610', 'name': 'flir'},
        #     {'vat': '0454064819', 'name': 'gim'},
        #     {'vat': '0866039556', 'name': 'hict'},
        #     {'vat': '0478890483', 'name': 'hydroscan'},
        #     {'vat': '0444177945', 'name': 'ocas'},
        #     {'vat': '0473191041', 'name': 'barco'},
        #     {'vat': '0467667088', 'name': 'boplan'},
        #     {'vat': '0405502362', 'name': 'picanol'}
        #     #{'vat': '0563644135', 'name': 'hello customer'},
        #     #{'vat': '0803978263', 'name': 'legalfly'},
        #     #{'vat': '0702877935', 'name': 'novable'},
        #     #{'vat': '0478493179', 'name': 'ixor'},
        #     #{'vat': '0794564414', 'name': 'jelloow'},
        #     #{'vat': '0745522501', 'name': 'nannyml'},
        #     #{'vat': '0537905085', 'name': 'iretailcheck'},
        #     #{'vat': '0818030890', 'name': 'foodpairing'},
        #     #{'vat': '0720636061', 'name': 'ArtiQ'},
        #     #{'vat': '0675758517', 'name': 'bingli'},
        #     #{'vat': '0475477964', 'name': 'vivansa'},
        #     #{'vat': '0742718508', 'name': 'segments.ai'},
        # ]
        
        implementors = self.kbo.get_kbo_implementors(self.month,self.year)
        
        current_time = datetime.datetime.now()
        print("Timestamp starting after kbo retrieval", current_time)
        #step 3: for every implementor -> use its denomination to scrape the page + get financial information with Staatsbladmonitor
        for element in implementors:
            current_time = datetime.datetime.now()
            print("Timestamp first implementor start", current_time)
            if self.debug:
                #Check if company has any AI relations
                print(f"Checking AI relations for {element['name']} \n")
            current_time = datetime.datetime.now()
            print("Timestamp checking if implementor is AI PRE", current_time)
            if (self.kbo_ai.check_companies(element['name']) ==1):
                if self.debug:
                    print("Company has AI relations! Started retrieving data for this company... \n")
                    current_time = datetime.datetime.now()
                    print("Timestamp checking if implementor is AI POST", current_time)
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
                        current_time = datetime.datetime.now()
                        print("Timestamp getting company logo PRE", current_time)
                        data['photo'] = self.company_scraper.get_company_logo(element['name'])
                        current_time = datetime.datetime.now()
                        print("Timestamp getting company logo POST", current_time)
                    except:
                        if self.debug:
                            print("something wrong with the logo fetcher")
                    data['vat'] = element['vat']

                    #scraped info
                    if self.debug:
                        print(f"time to generate the company page using openai: ")
                    current_time = datetime.datetime.now()
                    print("Timestamp generating company page OPENAI PRE", current_time)
                    scraped_info = self.company_scraper.generate_company_pages([element['name']])
                    current_time = datetime.datetime.now()
                    print("Timestamp generating company page OPENAI POST", current_time)
                    # sometimes openAI gives weird formats .. todo? prompt engineering xd
                    if len(scraped_info) != 6:
                        scraped_info = scraped_info[0]
                    if self.debug:
                        print(f"retrieved scraped data: {scraped_info}")
                    data['description'] = scraped_info[1]
                    current_time = datetime.datetime.now()
                    print("Timestamp scraped data DONE", current_time)
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
                    current_time = datetime.datetime.now()
                    print("Timestamp getting keypartners pages PRE", current_time)
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
                        if str(database_id) != 'www.companyweb.be' or str(database_id) != 'www.belgium.be':
                            data['links']['external_partner'].append(str(database_id))
                        else:
                            None
                    current_time = datetime.datetime.now()
                    print("Timestamp getting keypartners pages POST", current_time)

                    current_time = datetime.datetime.now()
                    print("Timestamp getting domain tags PRE", current_time)
                    for tag in scraped_info[5]:
                        data['links']['works_on'].append('domain_' + tag)
                    current_time = datetime.datetime.now()
                    print("Timestamp getting domain tags POST", current_time)
                    if self.debug:
                        print("financial information extraction:")
                    #financials:
                    current_time = datetime.datetime.now()
                    print("Timestamp getting financial info PRE", current_time)
                    financial = self.financial.StaadsbladMonitor(element['vat'])
                    current_time = datetime.datetime.now()
                    print("Timestamp getting financial info POST", current_time)
                    try:
                        data['zipcode'] = financial['zipcode']
                        data['street'] = financial['street']
                        data['street'] = data['street'].replace('é','e')
                        data['street'] = data['street'].replace('ë','e')
                        data['housenumber'] = financial['housenumber']
                        data['city'] = financial['city']
                        data['city'] = data['city'].replace('é','e')
                        data['city'] = data['city'].replace('ë','e')
                        data['startdate'] = financial['start date']
                        temp_financial = json.dumps(financial['financial'])
                        data['financial'] = temp_financial
                    except:
                        pass

                    if self.debug:
                        print("---------------------------------------------storing, time for next iteration--------------------------------------")
                    #step 4: -> store in file
                    file_path = "./data/" + element['name'] + ".json"

                    with open(file_path, 'w') as json_file:
                        json.dump(data, json_file, indent=4)
                    self.cosmos.write_to_graph()
                except Exception as e: #if something fails, no crash is needed, but store in the failed processes that can be retrieved
                    if self.debug:
                        print(f"fault!! {element['name']} -> {e}")
                    self.fails.append((element['name'], data))
            else:
                None

        #make all variables ready for the next time the update file gets called
        self.kbo_nr+=1
        self.year += (self.month==12)
        self.month = (self.month+1)%12


if __name__=="__main__":
    fetcher = fetcher(debug=False)
    fetcher.KBO_update()
