import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from collections import Counter
import csv
import time
import os
import json
import concurrent.futures
from threading import Thread
import functools

class KBO_AI:
    def __init__(self):
        pass

    def get_url_from_name(self,name):
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
    

    def get_soup(self,url):
        try:
            response = requests.get(url,timeout=5)
            soup = BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            
            return None
        return soup

    def get_links(self,soup, base_url):
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
                links.append(absolute_url)
        return links

    def related_ai_terms(self,base_url):
        ai_terms=[
        "artificial intelligence", "machine learning", " ml ", "deep learning",
        "neural network", "natural language processing", " nlp ",
        "data engineering", "feature engineering", "exploratory data analysis", 
        "feature extraction", "classification", "clustering", "time series analysis",
        "anomaly detection", "text mining", "web scraping","explainable",
        "genai", "generative ai", "knowledge representation", "design generator", "art generator", 
        "music generator", "text generator", "image generator", "creative ai",
        "pattern recognition", "data mining", "data science", "big data",
        "data analytics", "cognitive computing",
        "autonomous delivery","autonomous logistics", "autonomous vehicle", "autonomous labeling",
        "autonomous software", "autonomous system", "reinforcement learning", "genetic algorithm",
        "computer vision", "expert system", "fuzzy logic", "sentiment analysis", "virtual agent",
        "intelligent agent", "decision support system", 
        "automated reasoning", "swarm intelligence", "evolutionary computation", "smart grid",
        "ambient intelligence","data visualization", "business intelligence", "machine translation", "emotion ai",
        "cognitive computing", "neuromorphic", "brain-inspired", "biomimetic", "ai hardware",
        "ai chip", "ai processor", "ai accelerator", "edge ai", "ai coprocessors", "data generation",
        "data synthesis", "data simulation"
        ]
        if(base_url.endswith('.ai') or base_url.endswith('.ai/')):
            return True
        visited = set()
        ai_related_terms=[]
        pages_to_visit = [base_url]
        all_text = []
        ai_related_terms_page=[]
        start_time = time.time()  # Start the timer
        ai_term_counter=0
        
        while pages_to_visit:
            if time.time() - start_time > 30:
                    break
            url = pages_to_visit.pop(0)
            if url not in visited:
                visited.add(url)
                soup=self.get_soup(url)
                if(soup==None):
                    continue
                text = soup.get_text(separator='\n').lower()
                ai_related_terms_page = [term for term in ai_terms if term in text]
                ai_term_counter+=int(" ai " in text)
                if(len(ai_related_terms_page)!=0 or ai_term_counter>3):
                    #print(ai_related_terms_page)
                    return True
                links = self.get_links(soup, base_url)
                pages_to_visit.extend(links)
        return False

    def check_companies(self,name):
        base_url=self.get_url_from_name(name)
        if(base_url==None):
            return 2
        is_in_ai=self.related_ai_terms(base_url)
        return int(is_in_ai)

if __name__=="__main__":
    KBO_AI=KBO_AI()
    KBO_AI.check_companies("Biolizard")