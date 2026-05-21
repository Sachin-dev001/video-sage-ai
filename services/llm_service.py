from langchain_google_genai import ChatGoogleGenerativeAI


def get_chat_model():

    primary_model = "gemini-2.5-flash"
    fallback_model = "gemini-2.0-flash"

    try:

        llm = ChatGoogleGenerativeAI(
            model=primary_model,
            temperature=0.3,
            streaming=True
        )

        return llm

    except Exception:

        llm = ChatGoogleGenerativeAI(
            model=fallback_model,
            temperature=0.3,
            streaming=True
        )

        return llm