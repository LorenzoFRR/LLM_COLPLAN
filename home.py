import time
import streamlit as st
from utils import cria_chain_conversa, PASTA_ARQUIVOS


def sidebar():

    # Alterado para aceitar JSON ao invés de CSV
    uploaded_json = st.file_uploader(
        'Importe aqui o arquivo de perguntas e respostas (.json)', 
        type=['.json'], 
        accept_multiple_files=False
    )
    if uploaded_json is not None:
        # Salvar o arquivo JSON na pasta PASTA_ARQUIVOS
        with open(PASTA_ARQUIVOS / uploaded_json.name, 'wb') as f:
            f.write(uploaded_json.read())

    # Upload de PDFs
    uploaded_pdfs = st.file_uploader(
        'Importe aqui o documento', 
        type=['.pdf'], 
        accept_multiple_files=True
    )
    
    if not uploaded_pdfs is None:
        # Limpa arquivos .pdf antigos
        for arquivo in PASTA_ARQUIVOS.glob('*.pdf'):
            arquivo.unlink()
        # Salva os novos PDFs
        for pdf in uploaded_pdfs:
            with open(PASTA_ARQUIVOS / pdf.name, 'wb') as f:
                f.write(pdf.read())
    
    # Botão para inicializar ou atualizar o chatbot
    label_botao = 'Inicializar ChatBot'
    if 'chain' in st.session_state:
        label_botao = 'Atualizar ChatBot'
    if st.button(label_botao, use_container_width=True):
        # Verifica se há arquivos .pdf
        if len(list(PASTA_ARQUIVOS.glob('*.pdf'))) == 0:
            st.error('Adicione arquivos .pdf para inicializar o chatbot')
        else:
            st.success('Inicializando o ChatBot...')
            cria_chain_conversa()
            st.rerun()


def chat_window():
    st.header('Ambiente de Teste ChatBot COLPLAN', divider=True)

    # Verifica se a chain foi inicializada
    if not 'chain' in st.session_state:
        st.error('Faça o upload de PDFs para começar')
        st.stop()
    
    chain = st.session_state['chain']
    memory = chain.memory

    # Carrega histórico de mensagens do chatbot
    mensagens = memory.load_memory_variables({})['chat_history']

    container = st.container()
    # Exibe o histórico de mensagens
    for mensagem in mensagens:
        chat = container.chat_message(mensagem.type)
        chat.markdown(mensagem.content)

    # Input para novas mensagens
    nova_mensagem = st.chat_input('Insira uma mensagem')
    if nova_mensagem:
        chat = container.chat_message('human')
        chat.markdown(nova_mensagem)
        chat = container.chat_message('ai')
        chat.markdown('Gerando resposta')

        resposta = chain.invoke({'question': nova_mensagem})
        st.session_state['ultima_resposta'] = resposta
        st.rerun()


def main():
    with st.sidebar:
        sidebar()
    chat_window()

if __name__ == '__main__':
    main()
