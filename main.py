import streamlit as st
from openai import OpenAI
import requests
import json

# Custom CSS styling
st.markdown(
    """
    <style>
    .model-title, .stSelectbox, .stCheckbox, .stExpander {
        position: fixed;
        left: 120px; 
        z-index: 1000;
        background-color: #0e1117;
    }
    
    .model-title {
        top: 130px;
        font-size: 2rem;
        margin-bottom: 10px;
    }
    
    .stSelectbox {
        top: 190px;
        width: 300px;
        padding: 2px;
        border-radius: 5px;
    }
    
    .stCheckbox {
        top: 240px;
    }
    
    .stExpander {
        top: 350px;
        width: 300px;
        background-color: #0e1117;
    }

    .stApp {
        padding-top: 150px;
        padding-left: 350px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

models = [
    "DeepSeek-R1", 
    "Meta-Llama-3-1-405B-Instruct-FP8",
    "nvidia-Llama-3-1-Nemotron-70B-Instruct-HF",
    "Meta-Llama-3-3-70B-Instruct"
]

# Fixed position elements
st.markdown('<div class="model-title">Choose model</div>', unsafe_allow_html=True)

left, right = st.columns([0.4, 0.6])

with left:
    selected_model = st.selectbox(
        "Choose model",
        models,
        key="selected_model",
        label_visibility="collapsed",
        index=models.index(st.session_state.get("selected_model", models[0]))
    )
    
    # Web search toggle
    web_search = st.checkbox(
        'Enable Web Search',
        value=False,
        key="web_search",
        help="Enable real-time web search capabilities"
    )

    # Expander with formatted text
    with st.expander("DeepSeek Info", expanded=False):
        st.markdown("""
            Everything between </think> and </think> is the model's "thoughts" trying to understand your prompt. 
            Everything after is the actual response.  

            If you want to support us, feel free to PayPal us any amount you wish:
            https://paypal.me/m10ai
              
            *Powered by Akash Network*  
        """)

# Initialize OpenAI client after model selection
client = OpenAI(
    api_key=st.secrets["AKASH_KEY"],
    base_url="https://chatapi.akash.network/api/v1"
)

def search_web(query):
    """Perform web search using Serper API"""
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': st.secrets["SERPER_API_KEY"],
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, headers=headers, data=payload)
    results = response.json()
    
    search_info = []
    if 'organic' in results:
        for result in results['organic'][:3]:
            search_info.append(f"Title: {result.get('title', '')}")
            search_info.append(f"URL: {result.get('link', '')}")
            search_info.append(f"Snippet: {result.get('snippet', '')}\n")
    
    return "\n".join(search_info)

# Chat history initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Web search context
    context = ""
    if st.session_state.web_search:
        with st.status("🌐 Searching the web..."):
            search_results = search_web(prompt)
            context = f"Web search results:\n{search_results}\n\nBased on this information: "
    
    full_prompt = f"{context}{prompt}"
    
    # Update displayed messages
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Create message stream
        stream = client.chat.completions.create(
            model=st.session_state.selected_model,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[:-1]
            ] + [{"role": "user", "content": full_prompt}],
            stream=True,
        )
        
        response = st.write_stream(stream)
    
    st.session_state.messages.append({"role": "assistant", "content": response})