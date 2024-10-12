import streamlit as st

MODEL_NAME = 'gpt-3.5-turbo-0125'
RETRIEVAL_SEARCH_TYPE = 'mmr'
RETRIEVAL_KWARGS = {"k": 5, "fetch_k": 20}
PROMPT = '''Você é um assistente que auxilia o usuário na interação com um software de S&OP (Sales and Operations Planning).
            São fornecidos a você dois documentos de referência: Um arquivo pdf com observações e descrições sobre a ferramenta, segmentado por
            seções de acordo com a estrutura do software.
            Seu papel é, portanto, fornecer respostas ao usuário quanto às funcionalidades da ferramente.
            Se você não souber a resposta do que foi perguntado, simplesmente responda que não sabe. Não tente inventar a resposta.
            Aqui está um exemplo de interação. Você deverá seguir este tipo de resposta:
            Pergunta do usuário: Como faço para ver os códigos de canais e produtos?
            Resposta: No menu 'Dados' existe submenus de 'Hierarquia de Canal' e 'Hierarquia de Produto'. Acessando estes submenus, podem ser verificados os códigos de cada categoria


Contexto:
{context}

Conversa atual:
{chat_history}
Human: {question}
AI: '''

def get_config(config_name):
    if config_name.lower() in st.session_state:
        return st.session_state[config_name.lower()]
    elif config_name.lower() == 'model_name':
        return MODEL_NAME
    elif config_name.lower() == 'retrieval_search_type':
        return RETRIEVAL_SEARCH_TYPE
    elif config_name.lower() == 'retrieval_kwargs':
        return RETRIEVAL_KWARGS
    elif config_name.lower() == 'prompt':
        return PROMPT