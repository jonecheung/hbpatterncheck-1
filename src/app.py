"""
Hemoglobin Pattern Disease Chatbot - Streamlit UI
Main application interface
"""

import streamlit as st
from pathlib import Path
import os

# Page configuration
st.set_page_config(
    page_title="HB Pattern Chatbot",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .reference-card {
        padding: 0.5rem;
        border: 1px solid #ddd;
        border-radius: 0.3rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s;
    }
    .reference-card:hover {
        background-color: #f0f0f0;
        border-color: #1f77b4;
    }
    .stat-box {
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        text-align: center;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "reference_view" not in st.session_state:
    st.session_state.reference_view = "gallery"

# Helper function to get reference folders
def get_reference_folders():
    """Get list of reference chromatograph folders"""
    base_path = Path(__file__).parent.parent / "data" / "reference_chromatographs"
    
    folders = []
    if base_path.exists():
        for folder in sorted(base_path.iterdir()):
            if folder.is_dir():
                pdf_count = len(list(folder.glob("*.pdf")))
                folders.append({
                    "name": folder.name,
                    "display_name": folder.name.replace("_", " ").title(),
                    "path": folder,
                    "count": pdf_count
                })
    return folders

# Helper function to format category names
def format_category_name(name):
    """Format category name for display"""
    return name.replace("_", " ").title()

# Main header
st.markdown('<div class="main-header">🔬 Hemoglobin Pattern Disease Chatbot</div>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Mode selection
    mode = st.radio(
        "Mode:",
        ["💬 Chat", "📚 Reference Library", "📊 Statistics"],
        index=0
    )
    
    st.markdown("---")
    
    # Search settings
    st.subheader("🔍 Search Settings")
    num_results = st.slider("Number of results", 1, 10, 5)
    similarity_threshold = st.slider("Similarity threshold", 0.0, 1.0, 0.7, 0.05)
    
    st.markdown("---")
    
    # Reference categories
    st.subheader("📁 Reference Categories")
    reference_folders = get_reference_folders()
    
    if reference_folders:
        total_pdfs = sum(f["count"] for f in reference_folders)
        st.info(f"**Total:** {len(reference_folders)} categories, {total_pdfs} PDFs")
        
        # Show categories as expandable list
        with st.expander("View Categories", expanded=False):
            for folder in reference_folders:
                st.write(f"• **{folder['display_name']}** ({folder['count']})")
    else:
        st.warning("No reference folders found")
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    if st.button("🔄 Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("📥 Export Results", use_container_width=True):
        st.info("Export feature coming soon!")

# Main content area
if mode == "💬 Chat":
    # Chat interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Chat Interface")
        
        # Example queries
        st.markdown("**Try these example queries:**")
        example_cols = st.columns(2)
        
        with example_cols[0]:
            if st.button("What is HbE disease?", use_container_width=True):
                st.session_state.messages.append({
                    "role": "user",
                    "content": "What is HbE disease?"
                })
        
        with example_cols[1]:
            if st.button("Show elevated HbA2 cases", use_container_width=True):
                st.session_state.messages.append({
                    "role": "user",
                    "content": "Show elevated HbA2 cases"
                })
        
        st.markdown("---")
        
        # Display chat messages
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f"""
                        <div class="chat-message user-message">
                            <strong>👤 You:</strong><br>{message["content"]}
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="chat-message assistant-message">
                            <strong>🤖 Assistant:</strong><br>{message["content"]}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Show sources if available
                    if "sources" in message:
                        with st.expander("📚 View Sources"):
                            for source in message["sources"]:
                                st.write(f"• {source}")
        
        # Chat input
        st.markdown("---")
        user_input = st.chat_input("Ask about hemoglobin patterns...")
        
        if user_input:
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Mock assistant response (will be replaced with real AI)
            mock_response = f"""Based on the database, here's what I found about your query "{user_input}":

This is a **mockup response**. In the full system, this will:
- Search the vector database for relevant cases
- Retrieve similar chromatograph patterns
- Use OpenRouter LLM to generate detailed responses
- Cite specific page numbers and cases

**Features being implemented:**
✅ Vector database search
✅ OpenRouter integration
✅ Reference pattern matching
✅ Source citations"""
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": mock_response,
                "sources": [
                    "Page 12: Similar HbE pattern",
                    "Page 23: Elevated HbA2 reference",
                    "Page 45: Beta thalassemia case"
                ]
            })
            
            st.rerun()
    
    with col2:
        st.subheader("🖼️ Image Upload")
        st.info("Upload a chromatograph image for analysis")
        
        uploaded_file = st.file_uploader(
            "Choose an image...",
            type=["png", "jpg", "jpeg", "pdf"],
            help="Upload a chromatograph image or PDF"
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
            
            if st.button("🔍 Analyze Pattern", use_container_width=True):
                st.success("Analysis feature coming soon!")
                st.info("""
                **This will:**
                1. Send image to OpenRouter Vision API
                2. Get detailed pattern description
                3. Search for similar patterns in database
                4. Display matching reference cases
                """)

elif mode == "📚 Reference Library":
    # Reference library view
    st.subheader("📚 Reference Chromatograph Library")
    st.write(f"Browse {len(reference_folders)} categories of reference patterns")
    
    # Category filter
    all_categories = ["All Categories"] + [f["display_name"] for f in reference_folders]
    selected_category = st.selectbox("Filter by category:", all_categories)
    
    st.markdown("---")
    
    # Display reference folders as cards
    if selected_category == "All Categories":
        display_folders = reference_folders
    else:
        display_folders = [f for f in reference_folders if f["display_name"] == selected_category]
    
    # Grid layout
    cols = st.columns(3)
    for idx, folder in enumerate(display_folders):
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"""
                    <div class="reference-card">
                        <h4>📁 {folder['display_name']}</h4>
                        <p><strong>{folder['count']}</strong> reference PDFs</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"View {folder['display_name']}", key=f"btn_{folder['name']}", use_container_width=True):
                    st.info(f"Opening {folder['display_name']} references...")
                    # In full implementation, this will show the PDF thumbnails

elif mode == "📊 Statistics":
    # Statistics view
    st.subheader("📊 Database Statistics")
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="stat-box">
                <h2>17</h2>
                <p>Reference Categories</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_refs = sum(f["count"] for f in reference_folders)
        st.markdown(f"""
            <div class="stat-box">
                <h2>{total_refs}</h2>
                <p>Reference PDFs</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="stat-box">
                <h2>46</h2>
                <p>Patient Cases (Database)</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Category breakdown
    st.subheader("📈 Reference Distribution")
    
    if reference_folders:
        import pandas as pd
        
        # Create dataframe for chart
        df = pd.DataFrame([
            {"Category": f["display_name"], "Count": f["count"]}
            for f in reference_folders
        ]).sort_values("Count", ascending=False)
        
        st.bar_chart(df.set_index("Category"))
        
        # Table view
        st.subheader("📋 Detailed Breakdown")
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        🔬 Hemoglobin Pattern Disease Chatbot | 
        Built with Streamlit & OpenRouter | 
        <a href="https://github.com" target="_blank">Documentation</a>
    </div>
""", unsafe_allow_html=True)

