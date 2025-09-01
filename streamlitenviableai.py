import streamlit as st
import openai
import os
import base64
import io
import time
import json
from datetime import datetime
import requests
from PIL import Image
import numpy as np

# Add your OpenAI API key here
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")  #  REPLACE THIS WITH YOU ACTUAL API KEY

# App configuration
st.set_page_config(
    page_title="Enviable AI - Ultimate Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Unique Color Theme: Deep Space Purple with Electric Blue accents
UNIQUE_COLORS = {
    "primary": "#6A0DAD",  # Deep purple
    "secondary": "#00CED1",  # Electric teal
    "accent": "#FF6B8B",       # Vibrant pink
    "background": "#0A0A1A",   # Space black
    "surface": "#1A1A2E",      # Dark blue surface
    "text": "#FFFFFF",         # White text
    "success": "#00FFAA",      # Electric green
    "warning": "#FFD700"       # Gold
}

# Beautiful CSS with unique color scheme and animations
st.markdown(f"""
<style>
    /* Main theme - Unique Space Theme */
    .stApp {{
        background: linear-gradient(135deg, {UNIQUE_COLORS['background']} 0%, #000033 100%);
        color: {UNIQUE_COLORS['text']};
    }}
    
    /* Header styling */
    .main-header {{
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(45deg, {UNIQUE_COLORS['secondary']}, {UNIQUE_COLORS['accent']}, {UNIQUE_COLORS['success']});
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 6s ease infinite;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 0 0 30px rgba(0, 206, 209, 0.5);
        font-family: 'Arial Rounded MT Bold', sans-serif;
    }}
    
    @keyframes gradientShift {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    
    /* Subheader */
    .sub-header {{
        text-align: center;
        color: {UNIQUE_COLORS['secondary']};
        font-size: 1.3rem;
        margin-bottom: 2rem;
        text-shadow: 0 0 15px {UNIQUE_COLORS['secondary']}80;
        animation: glow 2s ease-in-out infinite alternate;
    }}
    
    @keyframes glow {{
        from {{ text-shadow: 0 0 10px {UNIQUE_COLORS['secondary']}80; }}
        to {{ text-shadow: 0 0 20px {UNIQUE_COLORS['secondary']}, 0 0 30px {UNIQUE_COLORS['secondary']}80; }}
    }}
    
    /* Chat containers */
    .chat-container {{
        background: rgba(26, 26, 46, 0.95);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3),
                    inset 0 0 0 1px rgba(255,255,255,0.1);
        border: 2px solid {UNIQUE_COLORS['primary']}40;
        max-height: 60vh;
        overflow-y: auto;
    }}
    
    /* Message bubbles */
    .user-message {{
        background: linear-gradient(135deg, {UNIQUE_COLORS['primary']}, {UNIQUE_COLORS['accent']});
        color: white;
        padding: 15px 20px;
        border-radius: 20px 20px 5px 20px;
        margin-left: auto;
        max-width: 70%;
        margin-bottom: 15px;
        box-shadow: 0 5px 25px {UNIQUE_COLORS['primary']}60,
                    inset 0 1px 1px rgba(255,255,255,0.3);
        animation: slideInRight 0.4s ease;
        border: 1px solid rgba(255,255,255,0.2);
    }}
    
    .ai-message {{
        background: linear-gradient(135deg, {UNIQUE_COLORS['secondary']}, #008B8B);
        color: white;
        padding: 15px 20px;
        border-radius: 20px 20px 20px 5px;
        margin-right: auto;
        max-width: 70%;
        margin-bottom: 15px;
        box-shadow: 0 5px 25px {UNIQUE_COLORS['secondary']}60,
                    inset 0 1px 1px rgba(255,255,255,0.3);
        animation: slideInLeft 0.4s ease;
        border: 1px solid rgba(255,255,255,0.2);
    }}
    
    @keyframes slideInRight {{
        from {{ transform: translateX(50px); opacity: 0; filter: blur(10px); }}
        to {{ transform: translateX(0); opacity: 1; filter: blur(0); }}
    }}
    
    @keyframes slideInLeft {{
        from {{ transform: translateX(-50px); opacity: 0; filter: blur(10px); }}
        to {{ transform: translateX(0); opacity: 1; filter: blur(0); }}
    }}
    
    /* Thinking animation */
    .thinking-container {{
        display: flex;
        align-items: center;
        padding: 20px;
        background: rgba(106, 13, 173, 0.2);
        border-radius: 20px;
        margin: 15px 0;
        animation: pulse 2s infinite;
        border: 1px solid {UNIQUE_COLORS['primary']}40;
        backdrop-filter: blur(10px);
    }}
    
    @keyframes pulse {{
        0%, 100% {{ 
            opacity: 0.8; 
            transform: scale(0.98);
            box-shadow: 0 0 20px {UNIQUE_COLORS['primary']}30;
        }}
        50% {{ 
            opacity: 1; 
            transform: scale(1);
            box-shadow: 0 0 30px {UNIQUE_COLORS['primary']}60;
        }}
    }}
    
    .thinking-dots {{
        display: flex;
        gap: 8px;
    }}
    
    .thinking-dot {{
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: linear-gradient(135deg, {UNIQUE_COLORS['secondary']}, {UNIQUE_COLORS['success']});
        animation: bounce 1.5s infinite;
        box-shadow: 0 0 10px {UNIQUE_COLORS['secondary']};
    }}
    
    .thinking-dot:nth-child(2) {{ 
        animation-delay: 0.2s; 
        background: linear-gradient(135deg, {UNIQUE_COLORS['accent']}, {UNIQUE_COLORS['primary']});
    }}
    .thinking-dot:nth-child(3) {{ 
        animation-delay: 0.4s; 
        background: linear-gradient(135deg, {UNIQUE_COLORS['success']}, {UNIQUE_COLORS['secondary']});
    }}
    
    @keyframes bounce {{
        0%, 100% {{ transform: translateY(0); }}
        50% {{ transform: translateY(-12px); }}
    }}
    
    /* Buttons */
    .stButton button {{
        background: linear-gradient(135deg, {UNIQUE_COLORS['primary']}, {UNIQUE_COLORS['accent']});
        color: white;
        border: none;
        border-radius: 15px;
        padding: 14px 28px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 5px 20px {UNIQUE_COLORS['primary']}40;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }}
    
    .stButton button:hover {{
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 8px 30px {UNIQUE_COLORS['primary']}60,
                    0 0 20px {UNIQUE_COLORS['secondary']}40;
    }}
    
    /* Feature cards */
    .feature-card {{
        background: linear-gradient(135deg, rgba(106, 13, 173, 0.3), rgba(0, 206, 209, 0.2));
        backdrop-filter: blur(10px);
        padding: 25px;
        border-radius: 18px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 15px 0;
        transition: all 0.4s ease;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }}
    
    .feature-card:hover {{
        transform: translateY(-8px) scale(1.02);
        background: linear-gradient(135deg, rgba(106, 13, 173, 0.4), rgba(0, 206, 209, 0.3));
        box-shadow: 0 15px 35px rgba(0,0,0,0.3),
                    0 0 25px {UNIQUE_COLORS['secondary']}30;
    }}
    
    /* Avatar styling */
    .avatar {{
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, {UNIQUE_COLORS['primary']}, {UNIQUE_COLORS['accent']});
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        color: white;
        margin-right: 15px;
        animation: float 4s ease-in-out infinite;
        box-shadow: 0 0 25px {UNIQUE_COLORS['primary']}60;
        border: 2px solid rgba(255,255,255,0.3);
    }}
    
    @keyframes float {{
        0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
        33% {{ transform: translateY(-8px) rotate(2deg); }}
        66% {{ transform: translateY(4px) rotate(-2deg); }}
    }}
    
    /* Sidebar styling */
    .sidebar .sidebar-content {{
        background: linear-gradient(180deg, {UNIQUE_COLORS['surface']}, {UNIQUE_COLORS['background']});
        border-right: 2px solid {UNIQUE_COLORS['primary']}30;
    }}
    
    /* Text area styling */
    .stTextArea textarea {{
        background: rgba(26, 26, 46, 0.8);
        border: 2px solid {UNIQUE_COLORS['primary']}40;
        border-radius: 15px;
        color: {UNIQUE_COLORS['text']};
        padding: 15px;
        backdrop-filter: blur(10px);
    }}
    
    .stTextArea textarea:focus {{
        border-color: {UNIQUE_COLORS['secondary']};
        box-shadow: 0 0 20px {UNIQUE_COLORS['secondary']}40;
    }}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: rgba(26, 26, 46, 0.5);
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(135deg, {UNIQUE_COLORS['primary']}, {UNIQUE_COLORS['accent']});
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(135deg, {UNIQUE_COLORS['secondary']}, {UNIQUE_COLORS['success']});
    }}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'avatar_style' not in st.session_state:
    st.session_state.avatar_style = "default"
if 'voice_mode' not in st.session_state:
    st.session_state.voice_mode = False

# AI Functions
def get_ai_response(user_input):
    """Get response from OpenAI with thinking animation"""
    if OPENAI_API_KEY == "your_openai_api_key_here":
        return "🔑 Please add your OpenAI API key to enable AI features!"
    
    try:
        openai.api_key = OPENAI_API_KEY
        
        # Show thinking animation
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown(f'''
        <div class="thinking-container">
            <div class="thinking-dots">
                <div class="thinking-dot"></div>
                <div class="thinking-dot"></div>
                <div class="thinking-dot"></div>
            </div>
            <span style="margin-left: 15px; color: {UNIQUE_COLORS['secondary']}; font-weight: 600; text-shadow: 0 0 10px {UNIQUE_COLORS['secondary']}80;">Enviable AI is thinking...</span>
        </div>
        ''', unsafe_allow_html=True)
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are Enviable AI, the most advanced and desirable AI assistant. You're incredibly intelligent, creative, and helpful. Provide exceptional responses that make users feel they have the best AI experience possible."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=600,
            temperature=0.8
        )
        
        # Remove thinking animation
        thinking_placeholder.empty()
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"❌ Error: {str(e)}. Please check your API key."

def generate_image(prompt):
    """Generate image using DALL-E"""
    if OPENAI_API_KEY == "your_openai_api_key_here":
        return None, "Please add your OpenAI API key for image generation!"
    
    try:
        openai.api_key = OPENAI_API_KEY
        
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512",
            response_format="url"
        )
        
        return response['data'][0]['url'], None
        
    except Exception as e:
        return None, f"Image generation error: {str(e)}"

# Avatar customization
def get_avatar(style="default"):
    """Get custom avatar based on style"""
    avatars = {
        "default": "🚀",
        "friendly": "🌟",
        "creative": "🎨",
        "tech": "💫",
        "premium": "🔥"
    }
    return avatars.get(style, "🚀")

# Main application
def main():
    # Header with animated gradient
    st.markdown('<div class="main-header">🚀 Enviable AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">The Ultimate AI Experience Everyone Wishes They Had</div>', unsafe_allow_html=True)
    
    # Sidebar with features
    with st.sidebar:
        st.markdown("### 🎨 Customization")
        
        # Avatar selection
        st.markdown("**Choose Your AI Avatar:**")
        avatar_style = st.selectbox(
            "Avatar Style",
            ["default", "friendly", "creative", "tech", "premium"],
            index=0,
            label_visibility="collapsed"
        )
        st.session_state.avatar_style = avatar_style
        
        st.markdown("---")
        st.markdown("### 🚀 Quick Features")
        
        # Feature buttons
        if st.button("🖼️ Generate Image", use_container_width=True):
            st.session_state.image_prompt = st.text_input("Describe your vision:")
        
        if st.button("💡 Brainstorm", use_container_width=True):
            st.session_state.user_input = "Help me brainstorm innovative ideas!"
        
        if st.button("📚 Learn", use_container_width=True):
            st.session_state.user_input = "Teach me something fascinating today!"
        
        if st.button("🎨 Create", use_container_width=True):
            st.session_state.user_input = "Help me create something amazing!"
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Chat interface
        st.markdown("### 💬 Conversation")
        
        # Display messages with avatars
        if st.session_state.messages:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for msg in st.session_state.messages:
                if msg['role'] == 'user':
                    st.markdown(f'''
                    <div style="display: flex; align-items: center; justify-content: flex-end; margin-bottom: 15px;">
                        <div class="user-message">{msg["content"]}</div>
                        <div class="avatar">👤</div>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown(f'''
                    <div style="display: flex; align-items: center; margin-bottom: 15px;">
                        <div class="avatar">{get_avatar(st.session_state.avatar_style)}</div>
                        <div class="ai-message">{msg["content"]}</div>
                    </div>
                    ''', unsafe_allow_html=True)
            
            # Check if last message was an image request
            if st.session_state.messages and "generate" in st.session_state.messages[-1]["content"].lower() and "image" in st.session_state.messages[-1]["content"].lower():
                with st.spinner("🖌️ Creating your masterpiece..."):
                    image_url, error = generate_image(st.session_state.messages[-1]["content"])
                    if image_url:
                        st.image(image_url, caption="🎨 Generated Image", use_container_width=True)
                    elif error:
                        st.error(error)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Welcome message
            st.markdown(f'''
            <div class="chat-container" style="text-align: center; padding: 50px;">
                <div class="avatar" style="margin: 0 auto 25px auto; width: 100px; height: 100px; font-size: 40px; box-shadow: 0 0 40px {UNIQUE_COLORS['primary']}80;">
                    {get_avatar(st.session_state.avatar_style)}
                </div>
                <h3 style="color: {UNIQUE_COLORS['secondary']}; text-shadow: 0 0 15px {UNIQUE_COLORS['secondary']}80;">Welcome to Enviable AI! 🚀</h3>
                <p style="color: #CCCCCC;">The most advanced AI experience available</p>
                <p style="color: #999999;">What would you like to create today?</p>
            </div>
            ''', unsafe_allow_html=True)
        
        # Input area
        st.markdown("---")
        user_input = st.text_area(
            "💭 Your message:",
            placeholder="Type your message or say 'Generate an image of something amazing'...",
            height=120,
            key="user_input"
        )
        
        # Action buttons
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("🚀 Send Message", use_container_width=True):
                if user_input.strip():
                    st.session_state.messages.append({"role": "user", "content": user_input})
                    ai_response = get_ai_response(user_input)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    st.rerun()
        
        with col_btn2:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        
        with col_btn3:
            if st.button("✨ Surprise Me", use_container_width=True):
                st.session_state.preset_input = "Show me something truly extraordinary!"
                st.rerun()
    
    with col2:
        # Features panel
        st.markdown("### 🌟 Premium Features")
        
        st.markdown('''
        <div class="feature-card">
            <h4>🖼️ AI Image Generation</h4>
            <p>Create stunning visuals from text descriptions</p>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="feature-card">
            <h4>💡 Intelligent Conversations</h4>
            <p>Advanced GPT-4 powered discussions</p>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="feature-card">
            <h4>🎨 Creative Assistance</h4>
            <p>Writing, design, and content creation help</p>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="feature-card">
            <h4>🚀 Ultra-Fast Responses</h4>
            <p>Lightning quick AI processing</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Quick prompts
        st.markdown("### ⚡ Quick Prompts")
        quick_prompts = [
            "Generate an image of a futuristic city",
            "Explain quantum computing simply",
            "Help me write a creative story",
            "What's the future of AI?"
        ]
        
        for prompt in quick_prompts:
            if st.button(prompt, key=f"quick_{prompt}", use_container_width=True):
                prompt = st.text_input("Enter something:", key="user_prompt")
# remove or comment this line:
# st.session_state.user_input = prompt
                st.rerun()

# Run the app
if __name__ == "__main__":
    main()