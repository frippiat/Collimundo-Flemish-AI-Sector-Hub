import re
"""to summarize texts, was used while working with free openai"""
# import nltk #unused
# from nltk.corpus import stopwords #unused
from nltk.tokenize import sent_tokenize  # , word_tokenize #unused
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer

# nltk.download("punkt")
# nltk.download("stopwords")


def summarize_text(text, sentences_count=400):
    """extract the sentences_count most important sentences from the text"""
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(
        parser.document, sentences_count=sentences_count
    )  # Adjust the number of sentences in the summary as needed
    summary = " ".join(str(sentence) for sentence in summary)
    return summary

#TODO: also removes valuable characters (like '.' for summarization)
def clean_text(text):
    # Remove extra whitespaces
    cleaned_text = re.sub(r"\s+", " ", text)
    # Strip leading and trailing whitespaces
    cleaned_text = cleaned_text.strip()
    # Remove non-ASCII characters
    cleaned_text = ''.join(char for char in cleaned_text if ord(char) < 128)
    return cleaned_text

def remove_duplicates_and_join(text):
    # Tokenize the text into sentences
    sentences = sent_tokenize(text)

    # Remove duplicates by converting sentences to a set and back to a list
    unique_sentences = list(set(sentences))

    # Join the unique sentences back into a single text
    unique_text = " ".join(unique_sentences)

    return unique_text
