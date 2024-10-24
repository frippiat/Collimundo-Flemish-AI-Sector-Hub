#imports
import random
import time
import requests
from bs4 import BeautifulSoup



def search_portfolio(root):
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
            subpages = get_urls_from_seed(root, curr_url)
            for subpage in subpages:
                if subpage not in done and subpage not in todo:
                    #check if its not the url we are searching for:

                    todo.append(subpage)
            time.sleep(random.random() * 10 + 2)


    # Get all URLs from the root
    urls = get_urls_from_seed(root, root)

    # Search for portfolio-related keywords in the URLs
    portfolio_keywords = ["portfolio", "portefeuille", "investeringen", "invested", "participaties"] # add if you found other keywords that work
    portfolio_url = None

    for url in urls:
        for keyword in portfolio_keywords:
            if keyword in url.lower():
                portfolio_url = url
                break
        if portfolio_url:
            break

    return portfolio_url


def invest_list(portfolio_url):
    """
    Extracts the text of the HTML and returns a list of company names.

    Inputs:
    - portfolio_url: The URL of the page where the invested companies are listed

    Returns:
    - A list of company names
    """
    # Get text content from the portfolio URL
    text_content = get_text_from_url(portfolio_url)
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


#manual functionality testing:
if __name__ == "__main__":
    print(get_text_from_url("https://www.vlaio.be/nl/begeleiding-advies/financiering/risicokapitaal/zoek?f[0]=domains%3A526&page=5"))


"""chatgpt with a cost of 2000 tokens = 0.02 euro's["Balak",
 "Brantsandpatents",
 "New Vision",
 "Serax",
 "Copus Group",
 "Vanhaverbeke",
 "Blommaert Aluminium Constructions",
 "Twikit",
 "Construct Materials Group",
 "ESAS",
 "Bluebee"]
"""