from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def create_chunks(docs):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )

    final_chunks = []

    for doc in docs:

        split_texts = splitter.split_text(
            doc.page_content
        )

        for text in split_texts:

            final_chunks.append(
                Document(
                    page_content=text,
                    metadata={
                        "timestamp": doc.metadata.get(
                            "timestamp",
                            "00:00"
                        )
                    }
                )
            )

    return final_chunks