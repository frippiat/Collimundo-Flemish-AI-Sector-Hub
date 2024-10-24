from bs4 import BeautifulSoup
import requests
import csv
from urllib.parse import urlparse, urljoin

#TODO : vat number -> companyweb?
#TODO: discovered bug: e.g. boltzmann is part of silverfinn, but i guess we just store them in a file for human intervention
# as mentioned in the risk list
def get_url_from_name(name):
    """input = name of a company
       output = url of that company"""
    search = name + '+belgium+company'
    url = 'https://www.google.com/search'

    headers = {
        'Accept' : '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82',
    }
    parameters = {'q': search}

    content = requests.get(url, headers = headers, params = parameters).text
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
            else: #delete one occurance of the letter
                index = domain.find(letter)
                domain = domain[:index] + (index < len(domain)-1) * domain[index+1:]
        if permutation: return urlparse(link).scheme + "://" + urlparse(link).netloc

    return None



def read_company_names_from_csv(csv_file):
    company_names = []

    try:
        with open(csv_file, "r", newline="", encoding="utf-8-sig") as file:  # Use utf-8-sig to handle BOM
            reader = csv.reader(file)
            for row in reader:
                # Assuming the company names are in the first column of each row
                if row:  # Check if the row is not empty
                    company_name = row[0].strip()  # Remove leading/trailing whitespace
                    company_names.append(company_name)

        return company_names

    except FileNotFoundError:
        print("File not found:", csv_file)
        return None
    except Exception as e:
        print("Error:", e)
        return None

#tested with 20 ai company names: 100% accuracy..
if __name__=="__main__":
    do = False
    if do:
        # Example usage
        csv_file_path = "C:\\Users\\warre\\OneDrive - UGent\\1ste master\\design project\\2de semester\\data\\test.csv"
        company_names = read_company_names_from_csv(csv_file_path)
        for company in company_names:
            company_url = get_url_from_name(company)
            if company_url:
                print("URL for", company, ":", company_url)
            else:
                print("No URL found for", company)
    if not do:
        print(get_url_from_name("Milieuzorg Roeselaere en Menen, Menen"))


