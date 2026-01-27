# Web Interface for Autonomous Research Agent System

## 🌐 Frontend Features

The web interface provides a user-friendly way to interact with the research system:

### ✨ Key Features

1. **Simple Research Input**
   - Enter any research topic
   - One-click research initiation
   - Real-time progress indication

2. **Comprehensive Results Display**
   - Research summary with key statistics
   - Topic analysis and expansion
   - Discovered papers with relevance scores
   - Generated citations in multiple formats (BibTeX, APA, IEEE)
   - Identified research gaps with priorities

3. **Interactive Elements**
   - Collapsible citation formats
   - Paper cards with abstracts
   - Research gap categorization
   - Download functionality

4. **Research History**
   - View previous research sessions
   - Download past results
   - Track research over time

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install flask
# or
pip install -r requirements.txt
```

### 2. Start the Web Server
```bash
python app.py
# or
python start_web_interface.py
```

### 3. Open Your Browser
Navigate to: **http://localhost:5000**

## 📱 How to Use

### Step 1: Enter Research Topic
- Type any research topic in the input field
- Examples:
  - "Machine Learning for Climate Change"
  - "Graph Neural Networks in Drug Discovery"
  - "Natural Language Processing for Healthcare"

### Step 2: Start Research
- Click "Start Research" button
- Wait for the system to process (usually 30-60 seconds)
- Watch the progress indicator

### Step 3: Explore Results
- **Summary**: Overview of papers found, claims extracted, etc.
- **Topic Analysis**: How the system expanded your topic
- **Papers**: Discovered academic papers with relevance scores
- **Citations**: Ready-to-use citations in multiple formats
- **Research Gaps**: Identified opportunities for future research

### Step 4: Download Results
- Click "Download JSON" to get complete results
- Use citations directly in your papers
- Save research gaps for future exploration

## 🎯 What the System Does

### 1. **Paper Discovery**
- Searches ArXiv for relevant papers
- Ranks papers by relevance to your topic
- Extracts metadata (authors, year, venue, abstract)

### 2. **Citation Generation**
- Creates properly formatted citations
- Supports BibTeX, APA, IEEE formats
- Handles different publication types (journal, conference, preprint)

### 3. **Research Analysis**
- Extracts claims from paper abstracts
- Identifies contradictions between papers
- Detects research gaps and opportunities
- Suggests future research directions

## 📊 Example Workflow

1. **Input**: "Deep Learning for Medical Imaging"

2. **System Processing**:
   - Expands topic into subtopics (CNN, segmentation, diagnosis, etc.)
   - Searches for relevant papers
   - Extracts claims and metrics
   - Identifies research gaps

3. **Output**:
   - 10-50 relevant papers
   - Citations ready for use
   - Research gaps like "Limited evaluation on rare diseases"
   - Downloadable JSON with all results

## 🔧 Technical Details

### Backend API Endpoints
- `POST /research` - Perform research on a topic
- `GET /history` - Get previous research results
- `GET /download/<filename>` - Download result files

### File Storage
- Results saved in `output/` directory
- JSON format with complete research data
- Timestamped filenames for organization

### Performance
- Typical research time: 30-60 seconds
- Concurrent request handling
- Persistent memory for faster subsequent searches

## 🛠️ Customization

### Modify Search Parameters
Edit `config.py`:
```python
MAX_PAPERS_PER_SOURCE = 50  # Increase for more papers
CLAIM_CONFIDENCE_THRESHOLD = 0.5  # Adjust quality threshold
```

### Styling
- Edit `templates/index.html` for UI changes
- Uses Bootstrap 5 for responsive design
- Font Awesome icons included

### Add New Features
- Extend `app.py` for new endpoints
- Add JavaScript functions in the template
- Create new result visualization components

## 🔍 Troubleshooting

### Common Issues

1. **"Module not found" error**
   ```bash
   pip install flask
   ```

2. **Port already in use**
   - Change port in `app.py`: `app.run(port=5001)`

3. **No papers found**
   - Try broader search terms
   - Check internet connection for ArXiv access

4. **Slow performance**
   - Reduce `MAX_PAPERS_PER_SOURCE` in config
   - Use more specific topics

## 📈 Future Enhancements

- [ ] User authentication and saved searches
- [ ] Advanced filtering and sorting options
- [ ] Export to Word/PDF formats
- [ ] Integration with reference managers
- [ ] Collaborative research features
- [ ] Mobile-responsive improvements

## 🤝 Contributing

To add new features to the web interface:

1. Fork the repository
2. Create a new branch for your feature
3. Test the web interface thoroughly
4. Submit a pull request

The web interface makes the powerful research system accessible to everyone - no command line required!