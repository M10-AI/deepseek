import streamlit as st
from openai import OpenAI
import requests
import json

models = [
    "DeepSeek-R1", 
    "Meta-Llama-3-1-405B-Instruct-FP8",
    "nvidia-Llama-3-1-Nemotron-70B-Instruct-HF",
    "Meta-Llama-3-3-70B-Instruct"
]


with st.sidebar:
    tab1, tab2, tab3 = st.tabs(["Start", "Info", "About us"])

    with tab1:
        
        st.title("Choose model")

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

    with tab2:
 #       Expander with formatted text
        with st.expander("App Info", expanded=False):
            st.markdown("""This model is powered by the [Akash Chat API](https://chat.akash.network/) from [Akash Networks](https://akash.network/).  
                        
Everything between *<think>* and *</think>* is the model's "thoughts" trying to understand your prompt. 
Everything after is the actual response.  

Besides DeepSeek the app features:  
- Meta's Llama 3.1 405B parameter model  
- Nvidia's Nemotron 70B model  
- Meta's Llamas 3.3 70B model
                        
All models are equipped with Retrieval-Agumented Generation (RAG) to search the web.
                        
            """)

    with tab3:
        with st.expander("M10 AI: Student Association", expanded=False):
            st.markdown(
            """Positioning Gothenburg as Sweden's Premier AI Hub through:  
- Industry-aligned workshops  
- Open source projects  
- Academic-corporate partnerships""")

            st.divider()

            st.markdown("""
Support our mission:  
[
Contribute by PayPal
](
https://paypal.me/m10ai
) """)
            
            st.divider()

            st.markdown("""
  
Or connect with our growing network of AI enthusiasts and professionals:  """,        
        )
            st.markdown("""
<style>
.social-icon {
    width: 45px !important;  /* Adjust this value to change size */
    height: 45px !important;
    margin: 0 5px;          /* Space between icons */
    transition: transform 0.3s ease;
}
.social-icon:hover {
    transform: scale(1.1);
}
</style>

<div style="display: flex; justify-content: center; gap: 15px; margin: 20px 0;">
    <a href="https://www.linkedin.com/company/m10-ai" target="_blank">
        <img class="social-icon" src="https://cdn-icons-png.flaticon.com/256/174/174857.png" alt="LinkedIn">
    </a>
    <a href="https://linktr.ee/m10ai" target="_blank">
        <img class="social-icon" src="https://cdn.iconscout.com/icon/free/png-256/free-linktree-logo-icon-download-in-svg-png-gif-file-formats--social-brand-communication-company-pack-logos-icons-9631079.png" alt="LinkTree">
    </a>
    <a href="https://www.instagram.com/_m10ai_/" target="_blank">
        <img class="social-icon" src="https://cdn-icons-png.flaticon.com/256/2111/2111463.png" alt="Instagram">
    </a>
</div>
""", unsafe_allow_html=True)
            

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

st.image("noback.png", caption="Welcome to our DeepSeek clone")

# Chat history initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("What can I help you with?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Web search context
    context = ""
    if st.session_state.web_search:
#        with st.status("🌐 Searching the web..."):
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
