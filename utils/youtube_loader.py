from youtube_transcript_api import YouTubeTranscriptApi
from langchain_core.documents import Document
import re


def extract_video_id(url):

    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"

    match = re.search(pattern, url)

    if match:
        return match.group(1)

    return url


def format_timestamp(seconds):

    minutes = int(seconds // 60)
    secs = int(seconds % 60)

    return f"{minutes:02d}:{secs:02d}"


def get_transcript_documents(youtube_url):

    video_id = extract_video_id(youtube_url)

    ytt_api = YouTubeTranscriptApi()

    # GET ALL AVAILABLE TRANSCRIPTS
    transcript_list = ytt_api.list(video_id)

    # TRY MANUAL ENGLISH
    try:

        transcript = transcript_list.find_manually_created_transcript(
            ["en"]
        )

    # FALLBACK TO GENERATED ENGLISH / HINDI
    except:

        try:

            transcript = transcript_list.find_generated_transcript(
                ["en", "hi"]
            )

        # FALLBACK TO ANY AVAILABLE TRANSCRIPT
        except:

            transcript = next(iter(transcript_list))

    # FETCH TRANSCRIPT
    fetched_transcript = transcript.fetch()

    docs = []

    current_text = []

    window_start = 0

    for item in fetched_transcript:

        # SUPPORT BOTH OBJECT + DICT FORMATS
        try:
            start = int(item.start)
            text = item.text

        except:
            start = int(item["start"])
            text = item["text"]

        # CREATE NEW 10 SECOND WINDOW
        if start >= window_start + 10:

            docs.append(
                Document(
                    page_content=" ".join(current_text),
                    metadata={
                        "timestamp": format_timestamp(window_start)
                    }
                )
            )

            current_text = []

            window_start = start

        current_text.append(text)

    # FINAL CHUNK
    if current_text:

        docs.append(
            Document(
                page_content=" ".join(current_text),
                metadata={
                    "timestamp": format_timestamp(window_start)
                }
            )
        )

    return docs