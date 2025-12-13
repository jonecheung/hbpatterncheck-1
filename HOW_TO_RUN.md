# How to Run the Chatbot UI

## Quick Start

### 1. Install Streamlit (if not already installed)
```bash
pip3 install streamlit
```

### 2. Navigate to Project Directory
```bash
cd /Users/jc/Desktop/hbpatterncheck/hbpatterncheck
```

### 3. Launch the Application
```bash
streamlit run src/app.py
```

### 4. Open in Browser
The app will automatically open at: `http://localhost:8501`

If it doesn't open automatically, just open your browser and go to that URL.

---

## What You'll See

### 🎨 UI Features

#### Main Interface (3 Modes)
1. **💬 Chat Mode** (Default)
   - Chat interface with message history
   - Example query buttons
   - Image upload panel
   - Mock AI responses (real AI coming soon)

2. **📚 Reference Library**
   - Browse all 17 reference categories
   - View your 146 reference PDFs
   - Filter by category
   - Interactive cards for each folder

3. **📊 Statistics**
   - Database overview
   - Reference distribution chart
   - Detailed breakdown table

#### Sidebar
- ⚙️ **Settings:** Adjust search parameters
- 📁 **Categories:** Quick view of all 17 folders
- 🚀 **Quick Actions:** Clear chat, export results

---

## Current Status

### ✅ Working Now
- Beautiful UI layout
- Three viewing modes
- Reference folder detection
- Chat interface structure
- Image upload widget
- Statistics dashboard

### 🔄 Coming Soon (Need to Build)
- Real AI responses (OpenRouter integration)
- Vector database search
- Actual pattern analysis
- Source citations from database
- Image processing with Vision API

---

## Stopping the Application

Press `Ctrl + C` in the terminal where Streamlit is running.

---

## Troubleshooting

### Port Already in Use
```bash
# Kill existing Streamlit process
pkill -f streamlit

# Or use different port
streamlit run src/app.py --server.port 8502
```

### Module Not Found
```bash
# Install missing dependencies
pip3 install streamlit pandas
```

### Can't Find Reference Folders
Make sure you're running from the project root:
```bash
pwd  # Should show: /Users/jc/Desktop/hbpatterncheck/hbpatterncheck
```

---

## Next Steps

Once the UI is running and you're happy with the layout:

1. **Build Backend Components:**
   - PDF text extraction
   - Vector database creation
   - OpenRouter integration
   - Query engine

2. **Connect UI to Backend:**
   - Replace mock responses with real AI
   - Add actual search functionality
   - Implement image analysis
   - Show real source citations

3. **Enhance UI:**
   - Add PDF preview
   - Show chromatograph images
   - Add export functionality
   - Improve styling

---

## Screenshots

### Chat Mode
- Clean chat interface
- Example query buttons
- Image upload panel
- Source citations

### Reference Library
- Grid view of all categories
- Count of PDFs in each
- Interactive cards
- Category filtering

### Statistics
- Summary stats boxes
- Bar chart of distribution
- Detailed table view
- Database overview

---

**Enjoy exploring the UI!** 🎉

Once you're ready to add real functionality, we'll start building the backend components.

