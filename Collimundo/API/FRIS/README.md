# Collimundo FRIS API

## FRIS API
FRIS stands as the central repository and regional gateway showcasing research activities and researchers across Flanders. It houses a vast collection, featuring over 42,000 research projects, profiles of 85,000 researchers, and details on 458,000 scientific publications. It offers detailed information on research groups, individual researchers, and organizations within Flemish higher education institutions, including background details, affiliations, projects, and publications. This platform aligns perfectly with our information extraction needs about the Flemish academic world.
For a better understanding of the database’s extent, visit the FRIS database online user interface: Which information can you find in FRIS? Additional information can be found on their website.

## Data Collection
FRIS offers a free-to-use API enabling access to its database content. The API encompasses all information accessible within the database. The data is primarily offered in an XML-format or CSV format, but there are also a few extensions available for the use of JSON. In either case, both formats are convenient for us. Detailed information regarding API functionality and usage is available at the following links:FRIS IT-Infrastructure,API Access Commands. We plan to refresh our information from the FRIS database daily, requesting all relevant data concerning research, research groups, and researchers involved in artificial intelligence/sustainability research in Flanders.

## Ethical and Legal Considerations
FRIS allows the usage of its public data freely, which aligns with their goal of enhancing information visibility.

### References
https://www.researchportal.be/nl
https://www.ewi-vlaanderen.be/en/fris-flanders-research-information-space

## FRIS-API
Python file, used to statically retrieve the starting papers. But chose to scrape new ones instead of using the FRIS API because this seemed easier.

## FRis_scraper
A python script to scrape the latest paper on Artificial Intelligence 

- scrapes title, urls, researh groups of paper
- checks if research group exists already, else makes new one
- adds paper to the research groups

### Libraries
The zeep library has been used to import the Client function for calls on the wsdl url.
BeautifulSoup for the scraper to parse the html.
