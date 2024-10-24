import json
import requests
from bs4 import BeautifulSoup
import re
import os 
from Fetcher.collimundo_database import GremlinGraphManager


class FrisScraper:
    def __init__(self):
        self.databaseManager = GremlinGraphManager()

    def transform_title(self,title):
        """
        Transforms a given title by converting it to lowercase, removing punctuation and extra spaces,
        removing common English stop words, replacing spaces with hyphens (except when there's already a hyphen),
        and appending the base URL.

        Args:
            title (str): The title to be transformed.

        Returns:
            str: The transformed title with the base URL appended.

        """
        # Convert to lowercase
        transformed_title = title.lower()
        
        # Remove punctuation and extra spaces
        transformed_title = re.sub(r'[^\w\s-]', '', transformed_title)
        
        # Remove common English stop words
        stop_words = ['the', 'a', 'an', 'of', 'all', 'with', 'for', 'to', 'in', 'on', 'by']
        transformed_title = ' '.join(word for word in transformed_title.split() if word not in stop_words)

        # Replace spaces with hyphens except when there's already a hyphen between words
        transformed_title = '-'.join(part.replace(' ', '-') for part in transformed_title.split('-'))
        
        initial_words = transformed_title.split('-')
        # Append the base URL
        final_title = "https://researchportal.be/en/publication/" + transformed_title
        # Adjust the length to fit the constraint
        final_title=final_title[:125]
        for word in final_title[41:125].split('-'):
            if word not in initial_words:
                final_title=final_title[:125-len(word)-1]
        return final_title

    def group_exists(self,group_name, data):
            """
            Check if a group with the given name exists in the provided data.

            Parameters:
            - group_name (str): The name of the group to check.
            - data (list): The data containing information about groups.

            Returns:
            - bool: True if a group with the given name exists, False otherwise.
            """
            group_name_lower = group_name.strip().lower()
            for group in data:
                temp = group["name"].split(' (')[0].strip().lower() 
                if temp == group_name_lower:
                    return True
            return False
    
    # Function to add missing groups to the data
    def add_missing_groups(self,missing_groups, data):
        """
        Adds missing groups to the data list.

        Parameters:
        - missing_groups (list): A list of group names that are missing in the data.
        - data (list): The data list to which the missing groups will be added.

        Returns:
        None
        """
        for group_name in missing_groups:
            new_group = {
                "id": group_name,
                "name": group_name,
                "name_lower":group_name.strip().lower(),
                "description": group_name,
                "photo": "",
                "website": "",
                "email": "",
                "tel": "",
                "papers": []
            }
            data.append(new_group)

    def add_paper_to_groups(self,title, url, research_groups, json_file):
        

        # Open JSON file and load data
        with open(json_file, 'r+') as f:
            data = json.load(f)
            # Add missing groups if they don't exist
            for group_name in research_groups:
                if not self.group_exists(group_name, data):
                    self.add_missing_groups([group_name], data)
            # Add paper to respective groups
            for group_name in research_groups:
                for group in data:
                    temp = group["name"].split(' (')[0].strip().lower()
                    if temp == group_name.split(' (')[0].strip().lower():
                        paper_info = {"title": title, "url": url}
                        # Check if the paper already exists in the group's papers
                        group_json = json.loads(group["papers"])
                        if paper_info not in group_json and paper_info["title"]!="":
                            group_json.append(paper_info)
                        papers_json = json.dumps(group_json)
                        group["papers"]=papers_json
                        group_file_name = group_name.replace("/", "_").replace(":", " ") + ".json"
                        current_dir = os.path.dirname(__file__)
                        group_file_path = os.path.join(current_dir, "data", group_file_name)
                        with open(group_file_path, 'w', encoding='utf-8') as group_file:
                                json.dump(group, group_file, indent=4, ensure_ascii=False)
                        id = group["id"]
                        query = "g.V().has('actor','research').has('name','within'('{id}'))"
                        out = self.databaseManager.submit_query(query)
                        if len(out)!=0:
                            query_implementor_update = f"g.V().has('actor','research').has('name','within'('{id}')).property('papers', '{papers_json}')"
                            self.databaseManager.submit_query(query_implementor_update)
                            print(len(out))
                        if len(out)==0:
                            self.databaseManager.write_to_graph()
                            print(len(out))

            # Write back to the JSON file
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

    def get_research(self):
        url = "https://researchportal.be/en/search"
        params = {
            "f[0]": "fris_content_type:publication",
            "f[1]": "fris_publication_year:2024",
            "search_api_fulltext": "Artificial Intelligence",
            "items_per_page": 10,
            "sort": "fris_publication_date",
            "order": "desc",
            "page": 0
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            titles = []
            for title in soup.find_all('a', attrs={'rel': 'bookmark'}):
                titles.append(title.text)
        else:
            print("Error:", response.status_code)
        result = []
        title = titles[0]
        transformed_title = self.transform_title(title)
        response = requests.get(transformed_title)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            dois = []
            research_units = []  # List to store research units
            institutional_urls = []  # List to store institutional repository URLs
            
            # Find all spans with class "label" to identify the DOI
            for span in soup.find_all('span', class_='label'):
                if span.text.strip() == "DOI:":
                    doi_link = span.find_next_sibling('span', class_='info').find('a').get('href')
                    dois.append(doi_link)
                elif span.text.strip() == "Institutional Repository URL:":
                    institutional_url = span.find_next_sibling('span', class_='info').find('a').get('href')
                    institutional_urls.append(institutional_url)
            
            # Find all research units
            for item in soup.find_all('div', class_='view-id-related_info_organisation'):
                for unit in item.find_all('li'):
                    research_unit = unit.get_text(strip=True)
                    research_units.append(research_unit)
            
            if dois:
                result.append(titles[0])
                result.append(dois[0])
            else:
                print("DOI not found on the page.")
            
            if institutional_urls:
                for url in institutional_urls:
                    result.append(url)
            else:
                print("Institutional Repository URLs not found on the page.")
            
            if research_units:
                temp_research_units=[]
                for unit in research_units:
                    if '(' in unit:
                        temp_research_units.append(unit[:unit.find(' (')])
                    else:
                        temp_research_units.append(unit)
                    result.append(temp_research_units)
            else:
                print("Research units not found on the page.")
        else:
            print("Error:", response.status_code)

        current_dir = os.path.dirname(__file__)
        json_file_path = os.path.join(current_dir, "research_groups.json")
        paper_title = result[0]
        paper_url = result[1] if len(result[1])>=5 else result[2]
        research_groups = result[3]
        self.add_paper_to_groups(paper_title, paper_url, research_groups, json_file_path)
        return "Success"
# Example usage
if __name__ == "__main__":
    Fris = FrisScraper()
    Fris.get_research()
