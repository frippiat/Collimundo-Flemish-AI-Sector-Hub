import csv
import requests
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import requests
import random
#Note: The openai-python library support for Azure OpenAI is in preview.
      #Note: This code sample requires OpenAI Python library version 1.0.0 or higher.
import os
"""
from openai import AzureOpenAI


client = AzureOpenAI(
  azure_endpoint = "https://collimundo-ai-france.openai.azure.com/",
  api_key="133d235b49d8408aa721a81b2427b689",
  api_version="2024-02-15-preview"
)


message_text = [{"role":"system","content":"You are an AI assistant that helps people find information."},{"role":"user","content":"you do work?"}]

completion = client.chat.completions.create(
  model="collimundo-ai-exp1", # model = "deployment_name"
  messages = message_text,
  temperature=0.7,
  max_tokens=800,
  top_p=0.95,
  frequency_penalty=0,
  presence_penalty=0,
  stop=None
)

print(completion.choices[0].message)"""


def get_urls_from_seed(root, seed):
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
    reqs = requests.get(seed)  # Get HTML
  except:
    reqs = requests.get(seed, verify=False)
  soup = BeautifulSoup(reqs.text, 'html.parser')  # Parse HTML (split it in structural components)
  urls = []  # To store all URLs on the same page
  for link in soup.find_all('a'):  # All hyperlink elements
    url = link.get('href')

    urls.append(url)
  return urls

print(get_urls_from_seed("https://techwolf.com/", "https://techwolf.com/"))