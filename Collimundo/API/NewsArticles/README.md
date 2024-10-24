# Collimundo NewsArticles API

## GDELT API

GDELT provides access to global news events and coverage in multiple languages, analyzing articles worldwide. URLs are exrtacted using gdelt Python library and sent into newspaper3k where desired information can be extracted from the articles based on their urls. With gdelt, it has been made possible to filter the articles based on keywords and countries.

## Data Collection
We utilize GDeltPyR, a Python library, for efficient data extraction, primarily opting for JSON format. We will provide a feed with the news articles with a picture and a title. If the users clicks on it, they will be redirected to the news article site. We will not show the article itself on our site.

## Ethical and Legal Considerations
We comply with GDPR regulations, ensuring that data extraction is limited to non-sensitive, publicly available information.

### References
https://www.gdeltproject.org/data.html

## VRT XML feed
Retrieving live articles from VRT headlines.

### Data Collection
Making a request to this XML URL to retrieve the headlines in Flanders.

### Ethical and Legal Considerations
Our usage of VRT complies with their feed usage instructions and legal terms.

### References
https://www.vrt.be/nl/info/gebruiksvoorwaarden/

## NewsArticles.py
Script that needs to be run hourly, retrieves news from the Gdelt API. The Gdelt API calls are quite costly (taking around 1 minute for the list of news based on keywords), so news will be saved in JSON files hourly to save time and make this unnoticable. 
The script also contains the retrieval of VRT headlines.

### Libraries
Installed libraries:
The Gdelt library has been used. This library has to be installed first using pip install gdelt.
The newspaper library from newspaper3k package has been used to extract information of an article using its url. This library can be installed using pip install newspaper3k.
Nltk needed to be installed to avoid errors.
Xmltodict was need to transform the XML file of VRT to a JSON file.
