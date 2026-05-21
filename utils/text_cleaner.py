import re


def clean_transcript(text):

    text = re.sub(r'\s+', ' ', text)

    text = re.sub(r'\[.*?\]', '', text)

    return text.strip()