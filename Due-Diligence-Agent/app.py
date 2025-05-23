import streamlit as st
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools import DuckDuckGoSearchResults
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from langchain_community.vectorstores import FAISS
import os
import time
from langchain.docstore.document import Document
from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="mxbai-embed-large")



model = OllamaLLM(model="deepseek-r1:1.5b")

template = """
You are an due delligent exeprt in answering questions about people and company's

Here are some relevant information: {context}

Here is the question to answer: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model



if 'kb' not in st.session_state:  # Initialize kb variable in session state
    st.session_state.kb = None

if 'db' not in st.session_state:  # Initialize kb variable in session state
    st.session_state.db = None

def get_urls(query, slider_valuex):
    knowledge_base = {}
    
    numbx = int(slider_valuex/2)
    numby = slider_valuex - numbx

    results = DDGS().text(query, max_results=numbx)
    for result in results:
        url = result["href"]
        # Store the rest of the info as the value
        knowledge_base[url] = {
            "title": result["title"],
            "source": result["href"],
        }

    with DDGS() as ddgs:
        news_results = ddgs.news(query, max_results=numby)
        for result in news_results:
            url = result["url"]
            # Store the rest of the info as the value
            knowledge_base[url] = {
                "title": result.get("title"),
                "source": result.get("source"),

            }
    return knowledge_base



def create_database(knowledge_base, database_name):
    for key,val in knowledge_base.items():
        try:
            r = requests.get(key, auth=('user', 'pass'))
            soup = BeautifulSoup(r.text, 'html.parser')
            paragraphs = soup.find_all('p')
            to_add = ""
            for para in paragraphs:
                  to_add+=para.text
            knowledge_base[key]['content'] =  to_add
        except:
            print(key)

    print("here is the dict", knowledge_base)

    data = []
    for key,val in knowledge_base.items():
        #print(knowledge_base[key]["content"])
        datax = Document(page_content= knowledge_base[key]["content"], metadata={"title": knowledge_base[key]['title'], "source": knowledge_base[key]['source']})
        data.append(datax)

    knowledge = FAISS.from_documents(data, embeddings)
    knowledge.save_local("vector database/"+database_name)


def get_response(query, database):
    hello = FAISS.load_local("vector database/"+database, embeddings, allow_dangerous_deserialization=True)
    x = hello.similarity_search_with_score(query, k = 2)
    sources = []
    contexts = ""
    for i in range(len(x)):
            content = x[i][0].page_content
            print(content)
            print()
            print()
            contexts+="\n\n"+content
            sources.append(x[i][0].metadata)

    result = chain.invoke({"context": contexts, "question": query})
    return result + str(sources)



# Initial setup
# Custom CSS to make the label larger
st.markdown("""
    <style>
        .big-text {
            font-size: 24px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

st.session_state.setdefault("current_index", 0)
st.session_state.setdefault("responses", {})
st.session_state.setdefault("updated_list", [])
st.session_state.setdefault("started", False)
# Set the page config at the very beginning
st.title("Welcome to Due Delligence App!")





# List of names
names_list = [f for f in os.listdir("vector database") if os.path.isdir(os.path.join("vector database", f))]

st.markdown('<p class="big-text">Selct an Existing Knowledge Base</p>', unsafe_allow_html=True)
# Display radio buttons to choose a name
selected_name = st.radio("Choose one from below list", names_list)

import re


# Step 1: Ask the user a question to begin
if not st.session_state.started:
    user_input = st.text_input('create a knowledgebase', placeholder="enter person/organization's name here...")
    
    slider_valuex = st.slider(
	    label='Number of web source',   # Label for the slider
	    min_value=0,               # Minimum value
	    max_value=100,             # Maximum value
	    value=10,                  # Default value
	    step=1                     # Step size
	)

    start_button = st.button("Start")

    if start_button and user_input:
        #kb = get_urls(user_input)
        st.session_state.kb = get_urls(user_input, slider_valuex)
        #print(kb)
        st.session_state.started = True
        st.session_state.user_name = user_input
        #st.subheader(f"Hello {st.session_state.user_name}, let's begin!")
        st.experimental_rerun()  # Rerun to proceed with the URL processing
else:
    st.subheader(f"For {st.session_state.user_name}, let's select some knowledge source!")
    # Step 2: Process the URLs and ask about each website
    url_list = list(st.session_state.kb.keys())

    if st.session_state.current_index < len(url_list):
        current_url = url_list[st.session_state.current_index]

        # Display website using iframe
        st.markdown(f"""
            <iframe src="{current_url}" width="100%" height="500"></iframe>
        """, unsafe_allow_html=True)

        st.write(f"URL: {current_url}")
        st.write("Add this website to your knowledge base?")

        col1, col2 = st.columns(2)

        if col1.button("Yes"):
            st.session_state.responses[current_url] = "Yes"
            st.session_state.updated_list.append(current_url)  # Append to session state list
            st.session_state.current_index += 1
            st.experimental_rerun()  # Force rerun to display next URL

        if col2.button("No"):
            st.session_state.responses[current_url] = "No"
            st.session_state.current_index += 1
            st.experimental_rerun()  # Force rerun to display next URL

    else:
        st.success("All websites reviewed!")
        st.write("Your responses:")
        st.json(st.session_state.responses)
        st.write("✅ URLs added to knowledge base:")
        st.write(st.session_state.updated_list)

        database_name = st.text_input('Give your knowledge base a name', placeholder="enter name here...")
        # Step 3: Create a new knowledge base
        if st.button("Create Knowledge Base"):
            if database_name:
                trimmed_dict = {key: st.session_state.kb[key] for key in st.session_state.updated_list if key in st.session_state.kb}
                create_database(trimmed_dict, database_name)
                st.success(f"Knowledge base '{database_name}' created successfully!")
                st.write("Reload the app to see the changes")
                
            else:
                st.write("provide database name properly")




# Initialize session state for chat history if not already initialized
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Function to handle sending a message
def send_message():
    user_input = st.session_state.user_input
    if user_input:
        # Add user's message to chat history
        st.session_state.chat_history.append({"role": "user", "message": user_input})

        # Example bot response (replace with actual model call)
        bot_response = get_response(user_input, selected_name)

        # Extract <think> block
        if "<think>" in bot_response:
            think_match = re.search(r"<think>(.*?)</think>", bot_response, re.DOTALL)
            think_content = think_match.group(1).strip() if think_match else ""

        # Remove <think> block from visible response
            main_response = re.sub(r"<think>.*?</think>", "", bot_response, flags=re.DOTALL).strip()
        else:
            think_content = "This is not a reasoning model"
            main_response = bot_response

        # Add bot response with separate think content
        st.session_state.chat_history.append({
            "role": "bot",
            "message": main_response,
            "think": think_content
        })

        # Clear the input field
        st.session_state.user_input = ""

# Display chat header
st.markdown(f'<p class="big-text">Uncover Insights from <span style="color: green;">{selected_name}</span> knowledge base</p>', unsafe_allow_html=True)

# Display chat history
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(f"**You:** {chat['message']}")
    elif chat["role"] == "bot":
        st.markdown(f"**Bot:** {chat['message']}")
        if "think" in chat and chat["think"]:
            st.markdown(
                f"""
                <div style="background-color: #f0f0f0; padding: 10px; border-radius: 8px; margin-top: 5px;">
                    <strong>🤔 Thinking:</strong><br>{chat['think']}
                </div>
                """,
                unsafe_allow_html=True
            )

# 🔘 Clear chat button
if st.button("🧹 Clear Chat"):
    st.session_state.chat_history = []
# Text input field for user's message
st.text_input("Ask your Question", key="user_input", on_change=send_message)





 # Flag to track if the user started the process


 # Restart the app
