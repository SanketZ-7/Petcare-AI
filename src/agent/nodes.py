


from langchain_community.vectorstores import FAISS
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_community.tools import TavilySearchResults
from langchain_core.documents import Document

from src.core import config


class SimpleLogger:
    def info(self, msg, **kwargs):
        print(f"[INFO] {msg} | {kwargs}")
    def warning(self, msg, **kwargs):
        print(f"[WARN] {msg} | {kwargs}")
    def error(self, msg, **kwargs):
        print(f"[ERROR] {msg} | {kwargs}")
    def debug(self, msg, **kwargs):
        print(f"[DEBUG] {msg} | {kwargs}")

logger = SimpleLogger()


embeddings = MistralAIEmbeddings(
    model=config.EMBEDDING_MODEL,
    mistral_api_key=config.MISTRAL_API_KEY
)
llm = ChatMistralAI(
    model=config.LLM_MODEL,
    temperature=config.TEMPERATURE,
    mistral_api_key=config.MISTRAL_API_KEY
)
grading_llm = llm  # Use the same LLM for grading


vectorstore = None
retriever = None
index_path = str(config.FAISS_INDEX_PATH)

try:
    if config.FAISS_INDEX_PATH.exists():
        vectorstore = FAISS.load_local(
            index_path, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        retriever = vectorstore.as_retriever()
        logger.info("faiss_vector_store_loaded", path=index_path)
    else:
        logger.warning("faiss_vector_store_not_found", path=index_path, mode="web_search_only")
except Exception as e:
    logger.error("faiss_load_failed", error=str(e), mode="web_search_only")

web_search_tool = TavilySearchResults(k=config.SEARCH_K)




async def retrieve(state):
    """Retrieve documents from vector store based on the question."""
    logger.info("retrieving_documents", question=state["question"][:50])
    question = state["question"]
    
    if retriever:
        documents = await retriever.ainvoke(question)
        logger.info("documents_retrieved", count=len(documents))
    else:
        logger.warning("no_retriever_configured", mode="web_search")
        documents = []
    
    return {"documents": documents, "question": question}


async def grade_documents(state):
    """Grade retrieved documents for relevance to the question."""
    logger.info("grading_documents", doc_count=len(state["documents"]))
    question = state["question"]
    documents = state["documents"]
    
    prompt = PromptTemplate(
        template="""You are a grader assessing relevance of a retrieved document to a user question.
        If the document contains keywords related to the user question, grade it as relevant.
        Give a binary score 'yes' or 'no' to indicate whether the document is relevant.
        Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.

        Here is the retrieved document:\n ------- \n{document}\n ------- \nHere is the user question: {question}""",
        input_variables=["question", "document"],
    )
    
    structured_llm_grader = grading_llm.with_structured_output({
        "name": "grade_document",
        "description": "Grades the relevance of a document to a user question.",
        "parameters": {
            "type": "object",
            "properties": {
                "score": {
                    "type": "string",
                    "enum": ["yes", "no"],
                    "description": "Whether the document is relevant to the user question."
                }
            },
            "required": ["score"]
        }
    })
    
    web_search_needed = False
    filtered_docs = []
    
    for d in documents:
        prompt_val = prompt.invoke({"question": question, "document": d.page_content})
        grade = await structured_llm_grader.ainvoke(prompt_val)
        if grade["score"].lower() == "yes":
            logger.debug("document_relevant", content_preview=d.page_content[:50])
            filtered_docs.append(d)

    if not filtered_docs:
        logger.info("no_relevant_documents", action="web_search")
        web_search_needed = True
    else:
        logger.info("relevant_documents_found", count=len(filtered_docs))
    
    return {"documents": filtered_docs, "web_search_needed": web_search_needed}


async def generate(state):
    """Generate an answer using the LLM and retrieved context."""
    logger.info("generating_answer", doc_count=len(state["documents"]))
    question = state["question"]
    documents = state["documents"]
    
    prompt = PromptTemplate(
        template="""You are an expert pet care assistant. Use the following retrieved context to answer the user's question.
        If you don't know the answer from the context, say that you cannot find specific information in your knowledge base.
        Be concise and helpful.

        Question: {question}\nContext: {context}\nAnswer:""",
        input_variables=["question", "context"],
    )
    rag_chain = prompt | llm | StrOutputParser()
    generation = await rag_chain.ainvoke({"context": documents, "question": question})
    logger.info("answer_generated", length=len(generation))
    return {"generation": generation}


async def transform_query(state):
    """Transform the query for better web search results."""
    logger.info("transforming_query", original=state["question"][:50])
    question = state["question"]
    
    prompt = PromptTemplate(
        template="""You are generating search queries for a web search tool. I need to find information about the following user question.
        Convert it to 1-3 effective search queries. Return a single string where queries are separated by ' OR '.

        Original question: {question}""",
        input_variables=["question"],
    )
    query_generation_chain = prompt | llm | StrOutputParser()
    better_query = await query_generation_chain.ainvoke({"question": question})
    logger.info("query_transformed", new_query=better_query[:50])
    return {"question": better_query}


async def web_search(state):
    """Perform web search using Tavily."""
    logger.info("performing_web_search", query=state["question"][:50])
    question = state["question"]
    
    search_results = await web_search_tool.ainvoke({"query": question})
    web_content = "\n".join([d["content"] for d in search_results])
    documents = [Document(page_content=web_content)]
    logger.info("web_search_complete", results_count=len(search_results))
    return {"documents": documents}


async def check_topic(state):
    """Check if the query is related to pets/animals."""
    logger.info("checking_topic", query=state["question"][:50])
    question = state["question"]
    
    prompt = PromptTemplate(
        template="""You are a query classifier. Determine if the following user question is related to pets, animals, or veterinary care.
        If it is relevant, answer 'yes'.
        If it is not related (e.g., asking about cars, coding, history, general knowledge unrelated to animals), answer 'no'.
        
        Question: {question}""",
        input_variables=["question"],
    )
    
    classification_llm = llm.with_structured_output({
        "name": "check_topic",
        "description": "Checks if the topic is relevant to pets.",
        "parameters": {
            "type": "object",
            "properties": {
                "score": {
                    "type": "string",
                    "enum": ["yes", "no"],
                    "description": "Relevance yes/no"
                }
            },
            "required": ["score"]
        }
    })
    
    res = await classification_llm.ainvoke(prompt.invoke({"question": question}))
    is_relevant = res["score"].lower() == "yes"
    
    logger.info("topic_check_complete", is_relevant=is_relevant)
    
    if not is_relevant:
        return {
            "is_relevant": False, 
            "generation": "I specialize only in pet care and animal-related questions. I cannot assist with other topics."
        }
    return {"is_relevant": True}