#imports
# for multithreading the scraping : threading.Thread(target=loop1_10).start()
import threading
import time
from bs4 import BeautifulSoup
from AzureCommunication import AzureOpenAICommunication
from urllib.parse import urlparse, urljoin
import requests
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import ast

# modifiability

######################################################general useful functions for scraping##########################################
class scraper:
    def __init__(self, forbidden, languages, debug=False, driver=None):
        # the list of urls from which the scraper should not examine
        self.forbidden = forbidden
        self.driver = driver
        #to print out things
        self.debug = debug
        # languages we think websites can take
        self.languages = languages
        #headers to mimic a browser
        self.headers= [
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
                        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36 OPR/80.0.4170.63",
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.38",
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
                        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.84",
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    ]

    def __del__(self):
        if self.driver:
            self.driver.quit()

    def request(self, url):
        """to bypass the blockings, """
        return requests.get(url, headers={'User-Agent': random.choice(self.headers)})

    def useful_url(self, root, seed):
        """this is the page filterer defined by self.forbidden"""
        #if no URL
        if seed is None:
            if self.debug:
                print(f"no link: {seed}")
            return False
        # The links to automatically send an email/call, this is a problem since i cant treat this as regular url
        if "mailto:" in seed or 'tel:+' in seed:
            if self.debug:
                print(f"mail contraint: {seed}")
            return False

        # no need to inspect random files
        if seed.endswith(".pdf") or seed.endswith(".png") or seed.endswith(".jpg") or seed.endswith(".zip") or seed.endswith(".htm"):
            if self.debug:
                print(f"type constraint: {seed}")
            return False

        #privacy or cookie
        if "privacy" in seed or "cookie" in seed:
            if self.debug:
                print(f"privacy constraint: {seed}")
            return False

        #tutorial
        if "tutorial" in seed or "interview" in seed:
            if self.debug:
                print(f"tutorial constraint: {seed}")
            return False

        # shortcut to something in same page
        if '#' in urlparse(seed).path:  # Check if the URL has a fragment identifier
            if self.debug:
                print(f"inner link constraint: {seed}")
            return False

        # all steps in the path followed by this url to the specific location:
        paths = [x for x in urlparse(seed).path.split('/') if x != '']
        #hidden pdfs -> only when at the end
        if "certificate" in paths:
            if self.debug:
                print(f"pdf constraint: {seed}")
            return False

        # all the forbidden elements that are specific for this scraper
        for step in paths:
            if step.lower() in self.forbidden:
                if self.debug:
                    print(f"Constraint: {step} -> {seed}")
                return False


        #external path
        if urlparse(root).netloc != urlparse(seed).netloc: #for sure other language, or it is from another domain, which is another necessary filter.
            if self.debug:
                print(f"outgoing link constraint: {seed}")
            return False

        #other languages that are forbidden for this scraper
        if paths[0].lower() in self.languages:
            if self.debug:
                print(f"language constraint: {seed}")
            return False

        # default case = good URL, better to scrape a page more than to loose valuable information
        return True

    def get_urls_from_seed(self, root, seed):
        """
        to get all hyperlinks (URLS) to pages of same website mentioned on this html page

        input: seed == URL of current webpage, root == home page

        example usage:

        seed = 'https://www.lexcour.be'
        for url in get_urls_from_seed(seed):
            print(url)

        output:
        https://www.lexcour.be
        https://www.lexcour.be/homepagina
        https://www.lexcour.be/onze-specialisaties
        https://www.lexcour.be/onze-aanpak
        https://www.lexcour.be/ons-team
        https://www.lexcour.be/contact
        https://www.lexcour.be/nieuws
        ...
        """
        try:
            reqs = self.request(seed)  # Get HTML
        except:
            reqs = requests.get(seed, verify=False)
        soup = BeautifulSoup(reqs.text, 'html.parser')  # Parse HTML (split it in structural components)
        urls = []  # To store all URLs on the same page
        for link in soup.find_all('a'):  # All hyperlink elements
            url = link.get('href')
            if url:

                if url.startswith('/'):
                    if self.useful_url(root, root * (root.endswith("/") == False) + root[:-1] * (root.endswith("/") == True) + url):
                        urls.append(root * (root.endswith("/") == False) + root[:-1] * (root.endswith("/") == True) + url)
                else:
                    if self.useful_url(root, url):
                        urls.append(url)

        return urls

    def get_text_from_url(self, url):
        """input: URL of a webpage
        returns: all text on this html page retrieved with the url
        Used for scraping all information on webpages, so it can be used by a LLM
        """
        try:
            response = self.request(url)
            response.raise_for_status()  # Raise an HTTPError for bad responses
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text(separator=' ', strip=True)  # Use strip to remove excess white spaces

        # Extract and append hyperlink text, as this is useful information for social media etc.
        links = soup.find_all('a')
        # non-internal links are handy for information (contact, social media, ...)
        for link in links:
            if 'href' in links and link['href'] is not None and link['href'] not in text_content and not self.useful_url(url, link['href']):
                text_content += ' ' + link['href']

        return text_content

    def extract_all_useful_paths(self, root):
        """extract all possible paths from a website"""

        # while there are URLs in the to-do list:
        # pop a URL from to-do, append it to paths, and add all links on the HTML page if they are not yet in
        # the paths list (already done) AND they are internal links

        # Parse the root URL to extract the base URL
        parsed_root = urlparse(root)
        base_url = parsed_root.scheme + "://" + parsed_root.netloc

        # Initialize the list of paths to be crawled
        paths = []
        todo = [root]
        
        # Process URLs in the to-do list
        while todo:
            url = todo.pop()
            print(f"next: {url}")
            print(f"todo: {len(todo)}")
            paths.append(urlparse(url).path)  # Extract path and append to paths

            try:
                # Fetch the HTML content of the page
                response = self.request(url)
                html_content = response.text

                # Parse HTML using BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')

                # Find all links in the page
                for link in soup.find_all('a', href=True):
                    # Extract the URL and make it absolute
                    href = urljoin(base_url, link['href'])

                    # Check if the URL is internal and not already in the list
                    if urlparse(href).netloc == parsed_root.netloc and urlparse(href).path not in paths and href not in todo and self.useful_url(root, href):
                        todo.append(href)
                

            except Exception as e:
                print(f"Error processing {url}: {e}")
            #time.sleep(random.random() * 4 + 2)

        return paths

    def get_url_from_name(self, name):
        """input = name of a company
           output = url of that company"""
        search = name + '+belgium+company'
        url = 'https://www.google.com/search'

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82',
        }
        parameters = {'q': search}

        content = requests.get(url, headers=headers, params=parameters).text
        soup = BeautifulSoup(content, 'html.parser')
        search_results = soup.find(id='search').find_all('a')

        for result in search_results:
            link = result.get('href')
            if not link:
                continue
            domain = urlparse(link).netloc

            # e.g. site of biolizard is lizard.bio, so domain is now lizardbio, a "permutation", TODO: ok to just quickly check if all letters are there?
            permutation = True
            for letter in name.lower():
                if letter == " ":
                    continue
                if letter not in domain:
                    permutation = False
                    break
                else:  # delete one occurance of the letter
                    index = domain.find(letter)
                    domain = domain[:index] + (index < len(domain) - 1) * domain[index + 1:]
            if permutation: return urlparse(link).scheme + "://" + urlparse(link).netloc

        return None


##########################################################explicit scraper for company pages##########################################
class Company_Scraper:
    def __init__(self, forbidden= ["videos","images","industrial", "academy", "distributors", "article", "articles", "newsletters", "newsletter", "data-privacy-notice", "legal-terms", "legal-terms", "legality", "cookies", "cookie-statement", "certifications", "webinar", "webinars", "news_events", "tagged", "privacy-policy", "news", "insights", "nieuws", "blog", "podcast", "podcasts", "events", "event", "career", "careers", "jobs", "job", "privacy", "policies" ,"policy","pdf"],
                 languages = ["at","ve","uy","pa","pe","cl","co","do","br","cl","kz","cz","lu","ca","fr", "ko", "cs", "ro", "it", "ja", "nl", "es", "de", "dk", "se", "fi", "no", "pl", "ar", "bg", "zh", "hr", "da", "el", "he", "hi", "hu", "id", "lt", "mn", "pt", "ru", "sk", "sr", "sv", "th", "tr", "vi"], debug=False):
        # the list of urls from which we are sure we dont have to examine
        self.forbidden = forbidden

        #to use selenium
        self.driver = None

        #to print out things
        self.debug = debug

        # languages we think websites can take
        self.languages = languages

        # useful scrape functions:
        self.scraper = scraper(forbidden, languages, self.debug, self.driver)
        self.openAI = AzureOpenAICommunication()

    def get_scraper(self):
        return self.scraper

    def textgenerator(self, root, paths):
        """
        used to create a whole text "summary" of a website
        input: URL
        output: summary string

        uses the function get_urls_from_seed() to visit all subpages, and the function get_text_from_url for all summaries
        """
        summary = ""
        for path in paths:
            curr_url = root + path
            curr_summary = self.scraper.get_text_from_url(curr_url)

            # add summary of this page
            if curr_summary:
                summary += curr_summary

            time.sleep(random.random() * 1 + 2)

        return summary

    def ai_extract_useful_paths(self, paths):
        """There was already a determenistic filtering, but chatgpt can reduce the amount of links we have to visit even more"""
        paths_p1000 = []  # the token rate limit of 1000 .. only add elements till the total amount of tokens is around 950
        while paths:
            token_appr = 0  # curr token approximation
            p1000 = []
            while token_appr < 950 and paths:
                path = paths.pop()
                token_appr += (path.count('/') + path.count("-") + path.count("_")) * 3 / 4 + 3  # appr 4 tokens per word + buffer
                p1000.append(path)
            paths_p1000.append(p1000)
        #filter with several api calls
        ans = []
        for p1000 in paths_p1000:
            openai_paths = self.openAI.communicate("Your task is to analyze a list of paths and identify those that are likely to contain relevant information for the following purposes: "
                                                        "generating a short summary, extracting contact information, finding social media links, discovering key partners, "
                                                        "and determining domain tags of the company. Please return a list of paths that you believe may contribute to these objectives, excluding those that are clearly irrelevant. "
                                                        "If there are no useful links, only return ['/'], with no other explanation! If there are more than 5 paths, give only 5 paths", str(p1000))

            ans.extend(ast.literal_eval(openai_paths))
        if self.debug:
            print(ans)

        #dont forget to scrape the root
        if not '/' in openai_paths:
            openai_paths.append('/')
        return ans

    def company_page_generator(self, summary):
        """based on a summary, generate """
        # only 1000 tokens per minute ... about 1 token per 4 characters -> search for earliest punctuation mark
        splitted_company_pages = []
        while True:
            if len(summary) / 4 < 850:
                if self.debug:
                    print("short summary, jippie")
                company_page = self.openAI.communicate(
                    r'Extract the information in between "" from the provided text and return it in the provided structure: ["Name", "short summary of max 5 sentences", ["linkedin", "facebook", "instagram", "Twitter/X"], ["telefoonnumber", "email address"], ["List of key partners (no persons, only companies!)"], ["list of less than 5 most important domain tags of the company"]] If any information cannot be extracted, insert "" on the appropriate positions. Only add information that is clearly correct, as I provide only parts of the website! Only return the given structue, do not provide extra explanation!',
                    summary)
                splitted_company_pages.append(company_page)
                break
            # else: len summary > 900 * 4 = 3600 -> find last punctuation mark, lets hope no information is lost
            substring = summary[:3600]
            last_punctuation_index = substring.rfind('.')
            if last_punctuation_index == -1:
                last_punctuation_index = substring.rfind('!')
            if last_punctuation_index == -1:
                last_punctuation_index = substring.rfind('?')
            if last_punctuation_index != -1:
                if self.debug:
                    print("lets see how it goes...")
                company_page = self.openAI.communicate(
                    r'Extract the information in between "" from the provided text and return it in the provided structure: ["Name", "short summary", ["linkedin", "facebook", "instagram", "Twitter/X"], ["telefoonnumber", "email address"], ["List of key partners (no persons, only companies!)"], ["list of less than 5 most important domain tags of the company"]] . If any information cannot be extracted, insert "" on the appropriate positions.  Only add information that is clearly correct, as I provide only parts of the website! Do not provide extra explanation along with the list!',
                    substring[:last_punctuation_index + 1], debug=self.debug)
                splitted_company_pages.append(company_page)
                summary = summary[last_punctuation_index + 1:]
            else:
                # If no punctuation mark found, just split at 3500 characters
                company_page = self.openAI.communicate(
                    r'Extract the information in between "" from the provided text and return it in the provided structure: ["Name", "short summary", ["linkedin", "facebook", "instagram", "Twitter/X"], ["telefoonnumber", "email address"], ["List of key partners (no persons, only companies!)"],["list of less than 5 most important domain tags of the company"]]. If any information cannot be extracted, insert "" on the appropriate positions. Only add information that is clearly correct, as I provide only parts of the website! Do not provide extra explanation along with the list!',
                    substring, debug=self.debug)
                splitted_company_pages.append(company_page)
                summary = summary[3200:]

        ######## combine the results -> let chatgpt combine the results till there is only one list over
        while len(splitted_company_pages) > 1:
            curr = []
            while len(str(curr)) / 4 < 800 and len(splitted_company_pages) >= 1:
                curr.append(splitted_company_pages.pop())
            if self.debug:
                print(f"combining {len(curr)} instances to one, in big list still {len(splitted_company_pages)} instances")
            splitted_company_pages.append(ast.literal_eval(self.openAI.communicate('Combine multiple instances of the provided structure of a specific company into one consolidated list. Each instance is represented as a list with the following structure: ["Name (use most occurring)", "Short summary of less than 5 sentences (use only information that occurs in more than one summary of the structures!)", ["LinkedIn url", "Facebook url", "Instagram url", "Twitter/X url"], ["Telephone number", "Email address"], ["List of key partners (no persons, only companies!)"], ["List of maximum (!) 5 most important domain tags in the given structures"]] If only one instance is presented, return this instance as is without any extra explanation. For each position in the structure, inspect all information across all instances and extract the most important information. Please provide the combined information as a Python list without any additional explanation.', str(curr), debug=self.debug)))


        company_page = splitted_company_pages[0]

        try:
            company_description = company_page[1].replace("'"," ")

            company_page[1]= company_description

        except:
            pass

        #sometimes openAI gives weird formats .. todo? prompt engineering xd
        if len(company_page) != 6:
            company_page = company_page[0]


        # domain tags not always correct -> database has limited amount of tags
        with open('./input/domain_tags.txt', 'r') as file:
            # Read the entire contents of the file into a string
            domain_tags = file.read()
        subst = self.openAI.communicate('You are tasked with selecting the most appropriate substitute domain tags from a provided list of domain tags extracted from a companys website. You will be given two lists: 1) The extracted tags: A list of domain tags extracted from the company s website. This will be the user input. 2) The available tags: A list of domain tags available in the database. This can be found at the end of this message Your objective is to choose a maximum of 5 domain tags from the available tag list that best match the extracted tags. Please ensure that the selected tags are the most relevant substitutes based on the context provided. Please return your selection as a Python list containing the 5 chosen domain tags, without any additional explanations. The list of available tags:' + str(domain_tags), str(company_page[-1]), debug=self.debug)
        #todo: chatgpt is a spacer


        if not subst.startswith("["): subst = "[" + subst
        if not subst.endswith("]"): subst = subst + "]"

        company_page[-1] = ast.literal_eval(subst)

        return company_page
        """splitted = []  # combine till there is only one left
        while len(splitted > 1):
            to_combine = ""
            while len(to_combine) / 4 < 850:
                to_combine += " + " + splitted.pop()"""

    def generate_company_pages(self, companies):
        """input: list of company names and their btw number, returns: list of their appropriate
        company pages in appropriate format"""
        ans = []
        lock = threading.Lock()  # Lock to ensure thread-safe appending to ans list

        def scrape_single_comany(company):
            root = self.scraper.get_url_from_name(company)

            #step 1 : extract all useful links based on what we defined as useful links
            urls = self.scraper.extract_all_useful_paths(root)

            #step 2: extra filter these possible URLs using Azure OpenAI
            useful_urls = self.ai_extract_useful_paths(urls)

            #step 3: generate a full text summary of the info on these URLs
            summary = self.textgenerator(root, useful_urls )

            #step 4: get company page based
            company_page = self.company_page_generator(summary)

            return company_page

        # Create threads for each company and start them
        #threads = [] -> possibility to go multithreading once openAI licence is upgraded
        for company in companies:
            ans.append(scrape_single_comany(company))
            """thread = threading.Thread(target=scrape_single_comany, args=(company,))
            thread.start()
            threads.append(thread) todo: multithreading isnt possible with openai :((("""

        # Wait for all threads to complete
        """for thread in threads:
            thread.join()"""

        return ans

    def get_company_logo(self, name):
        #use google images
        search = name + '+belgium+company+logo'
        url = 'https://www.google.com/search?q=' + search
        parameters = {'q': search}
        self.driver = webdriver.Chrome()
        content = self.driver.get(url)
        time.sleep(5)
        #if some cookie to accept
        try:
            # Find the button to go to images
            button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="W0wltc"]')))
            button.click()
        except:
            None

        time.sleep(2)
        # Find the button to go to images
        button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="hdtb-sc"]/div/div/div[1]/div/div[2]/a/div')))

        #current text
        content = self.driver.page_source
        button.click()
        soup = BeautifulSoup(content, 'html.parser')
        search_results = soup.find_all('img')

        for element in search_results[1:]:
            src = element.get('src')
            if src and "google" not in element.get('alt').lower():
                return src
        self.driver.quit()

        return None


if __name__=="__main__":
    company = Company_Scraper(debug=True)
    print(company.get_company_logo("PolySense"))


