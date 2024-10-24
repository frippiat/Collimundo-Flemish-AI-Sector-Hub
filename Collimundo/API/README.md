# Collimundo APIs


From the Data Management Plan:

## GDELT (NewsArticles)

GDELT provides access to global news events and coverage in multiple languages, analyzing articles worldwide. URLs are exrtacted using gdelt Python library and sent into newspaper3k where desired information can be extracted from the articles based on their urls. With gdelt, it has been made possible to filter the articles based on keywords and countries.

Data Collection:We utilize GDeltPyR, a Python library, for efficient data extraction, primarily opting for JSON format. We will provide a feed with the news articles with a picture and a title. If the users clicks on it, they will be redirected to the news article site. We will not show the article itself on our site.

Ethical and Legal Considerations:We comply with GDPR regulations, ensuring that data extraction is limited to non-sensitive, publicly available information.


## Staatsbladmonitor (Staadsblad)

Staatsbladmonitor offers comprehensive information about Belgian enterprises, including financial data, key personnel, and publications. The query of these companies is based on their VAT number

Data Collection:We utilize their API to extract relevant company information in JSON format. One downside to using Staadsbladmonitor is that it lets you only use 100 tokens daily for the API. A way to get around this is to make more accounts. 2 tokens are needed for a company to extract all its public financial information from the past few years.

Ethical and Legal Considerations:Our usage of Staatsbladmonitor data complies with their API usage instructions and legal terms.

## Flanders Research Information Space (FRIS)

FRIS stands as the central repository and regional gateway showcasing research activities and researchers across Flanders. It houses a vast collection, featuring over 42,000 research projects, profiles of 85,000 researchers, and details on 458,000 scientific publications. It offers detailed information on research groups, individual researchers, and organizations within Flemish higher education institutions, including background details, affiliations, projects, and publications. This platform aligns perfectly with our information extraction needs about the Flemish academic world.

For a better understanding of the database’s extent, visit the FRIS database online user interface: Which information can you find in FRIS? Additional information can be found on their website:FRIS General Information.

Data Collection:FRIS offers a free-to-use API enabling access to its database content. The API encompasses all information accessible within the database. The data is primarily offered in an XML-format or CSV format, but there are also a few extensions available for the use of JSON. In either case, both formats are convenient for us. Detailed information regarding API functionality and usage is available at the following links:FRIS IT-Infrastructure,API Access Commands. We plan to refresh our information from the FRIS database daily, requesting all relevant data concerning research, research groups, and researchers involved in artificial intelligence/sustainability research in Flanders.

Ethical and Legal Considerations:FRIS allows the usage of its public data freely, which aligns with their goal of enhancing information visibility.
