from pathlib import Path
import json
import streamlit as st
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.vectorstores.faiss import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
from configs import *

_ = load_dotenv(find_dotenv())

PASTA_ARQUIVOS = Path(__file__).parent / 'arquivos'


class Document:
    def __init__(self, content, metadata):
        self.page_content = content
        self.metadata = metadata


def importacao_documentos():
    documentos = []
    # Importar PDFs
    for arquivo in PASTA_ARQUIVOS.glob('*.pdf'):
        loader = PyPDFLoader(str(arquivo))
        documentos_arquivo = loader.load()
        documentos.extend(documentos_arquivo)
    return documentos


def importacao_json():
    json_data = []
    json_file = list(PASTA_ARQUIVOS.glob('*.json'))

    if json_file:
        with open(json_file[0], 'r', encoding='utf-8') as f:
            data = json.load(f)
            if "perguntas_respostas" in data and isinstance(data["perguntas_respostas"], list):
                for idx, item in enumerate(data["perguntas_respostas"]):
                    pergunta_resposta = Document(
                        content=f"Pergunta: {item['pergunta']} Resposta: {item['resposta']}",
                        metadata={'source': json_file[0].name, 'doc_id': idx}
                    )
                    json_data.append(pergunta_resposta)
            else:
                st.error("Estrutura JSON inválida. Espera-se um dicionário com a chave 'perguntas_respostas' contendo uma lista de perguntas e respostas.")

    return json_data



def split_de_documentos(documentos):
    recur_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2500,
        chunk_overlap=250,
        separators=["/n\n", "\n", ".", " ", ""]
    )
    documentos = recur_splitter.split_documents(documentos)

    for i, doc in enumerate(documentos):
        doc.metadata['source'] = doc.metadata['source'].split('/')[-1]
        doc.metadata['doc_id'] = i
    return documentos

def cria_vector_store(documentos):
    embedding_model = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(
        documents=documentos,
        embedding=embedding_model
    )
    return vector_store



def cria_chain_conversa():
    documentos = importacao_documentos()
    documentos = split_de_documentos(documentos)

    # Importar perguntas e respostas do JSON
    json_data = importacao_json()
    # Certifique-se de que o JSON foi carregado corretamente
    if json_data:
        documentos.extend(json_data)

    vector_store = cria_vector_store(documentos)

    chat = ChatOpenAI(model=get_config('model_name'))
    memory = ConversationBufferMemory(
        return_messages=True,
        memory_key='chat_history',
        output_key='answer'
    )
    retriever = vector_store.as_retriever(
        search_type=get_config('retrieval_search_type'),
        search_kwargs=get_config('retrieval_kwargs')
    )
    prompt = PromptTemplate.from_template(get_config('prompt'))
    chat_chain = ConversationalRetrievalChain.from_llm(
        llm=chat,
        memory=memory,
        retriever=retriever,
        return_source_documents=True,
        verbose=True,
        combine_docs_chain_kwargs={'prompt': prompt}
    )

    st.session_state['chain'] = chat_chain
