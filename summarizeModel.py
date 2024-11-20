from bs4 import BeautifulSoup
from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


def split_text(text, max_length=2000):
    """
    Splits the text into parts with each part having at most `max_length` characters,
    ensuring it doesn't split in the middle of a word.
    """
    words = text.split()  # Split the text into words
    parts = []
    current_part = []

    for word in words:
        # Check if adding the next word exceeds the limit
        if len(' '.join(current_part + [word])) > max_length:
            # Save the current part and start a new one
            parts.append(' '.join(current_part))
            current_part = [word]
        else:
            # Add the word to the current part
            current_part.append(word)

    # Add the last part if it has any content
    if current_part:
        parts.append(' '.join(current_part))

    return parts


def getSummarization(text):
    """
    Extracts text from HTML content, splits it if necessary, and summarizes each part.

    Args:
        text (str): The HTML content to be processed.
        summarizer (function): A summarizer function, e.g., from Hugging Face Transformers.

    Returns:
        list: A list of summaries for each part of the text.
    """
    # Extract text from HTML
    soup = BeautifulSoup(text, 'html.parser')
    plain_text = soup.get_text(separator=" ", strip=True)

    # Split the text into manageable chunks
    text_parts = split_text(plain_text, max_length=2000)

    # Summarize each part
    summaries = []
    for part in text_parts:
        summary = summarizer(part, max_length=260, min_length=30, do_sample=False)
        summaries.append(summary)

    summariesFixed = [{"summary_text":""}]

    for el in summaries:
        summariesFixed[0]["summary_text"] += el[0]["summary_text"]

    return summariesFixed