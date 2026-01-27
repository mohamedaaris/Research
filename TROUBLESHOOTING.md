# Troubleshooting Guide

## Common Issues and Solutions

### 1. "Error: no running event loop"

**Problem**: This error occurs when Flask tries to run async code but there's no event loop.

**Solution**: Use the fixed version of the app:
```bash
python app_fixed.py
```

**Why it happens**: Flask runs synchronously, but our research system uses async/await. The fixed version handles this by running async code in separate threads.

### 2. Web Interface Not Loading

**Problem**: Browser shows "This site can't be reached" or similar error.

**Solutions**:
1. Make sure the server is running:
   ```bash
   python app_fixed.py
   ```

2. Check if the port is available:
   ```bash
   # On Windows
   netstat -an | findstr :5000
   
   # On Linux/Mac
   lsof -i :5000
   ```

3. Try a different port by editing `app_fixed.py`:
   ```python
   app.run(debug=True, host='0.0.0.0', port=5001)
   ```

### 3. Research Request Times Out

**Problem**: The research takes too long and times out.

**Solutions**:
1. Use more specific topics:
   - ❌ "Machine Learning"
   - ✅ "Graph Neural Networks for Drug Discovery"

2. Check internet connection (needed for ArXiv search)

3. Increase timeout in `app_fixed.py`:
   ```python
   results = future.result(timeout=600)  # 10 minutes
   ```

### 4. No Papers Found

**Problem**: Research completes but finds 0 papers.

**Solutions**:
1. Try broader search terms
2. Check if ArXiv is accessible
3. Use topics that are likely to have academic papers

### 5. Import Errors

**Problem**: "ModuleNotFoundError" when starting the server.

**Solutions**:
1. Install missing dependencies:
   ```bash
   pip install flask
   pip install -r requirements.txt
   ```

2. Make sure you're in the correct directory:
   ```bash
   ls  # Should show app_fixed.py, src/, templates/
   ```

### 6. Citations Not Generating

**Problem**: Papers are found but no citations are created.

**Solutions**:
1. Check if papers have proper metadata
2. Look at server logs for citation errors
3. Verify the citation builder agent is working

### 7. Slow Performance

**Problem**: Research takes very long to complete.

**Solutions**:
1. Reduce the number of papers searched in `config.py`:
   ```python
   MAX_PAPERS_PER_SOURCE = 20  # Reduce from 50
   ```

2. Use more specific topics
3. Check system resources (CPU, memory)

## Testing the System

### Quick Test
```bash
python test_web_api.py
```

### Manual Testing Steps

1. **Start the server**:
   ```bash
   python app_fixed.py
   ```

2. **Open browser**: http://localhost:5000

3. **Test basic functionality**:
   - Enter topic: "Deep Learning"
   - Click "Start Research"
   - Wait for results

4. **Check test endpoint**: http://localhost:5000/test

### Expected Behavior

1. **Topic Input**: Should accept any text
2. **Research Process**: Should show loading spinner
3. **Results Display**: Should show papers, citations, gaps
4. **Download**: Should generate JSON file
5. **History**: Should show previous searches

## Debug Mode

To get more detailed error information:

1. **Enable Flask debug mode** (already enabled in app_fixed.py)

2. **Check server logs** in the terminal where you started the server

3. **Check browser console** (F12 → Console tab) for JavaScript errors

## Performance Optimization

### For Faster Research:
```python
# In config.py
MAX_PAPERS_PER_SOURCE = 10  # Fewer papers
MAX_CONCURRENT_REQUESTS = 2  # Less parallelism
```

### For Better Results:
```python
# In config.py
MAX_PAPERS_PER_SOURCE = 100  # More papers
CLAIM_CONFIDENCE_THRESHOLD = 0.3  # Lower threshold
```

## System Requirements

### Minimum:
- Python 3.8+
- 2GB RAM
- Internet connection
- Modern web browser

### Recommended:
- Python 3.10+
- 4GB RAM
- Fast internet connection
- Chrome/Firefox/Safari

## Getting Help

### Check Logs
1. **Server logs**: Terminal where you ran `python app_fixed.py`
2. **Browser logs**: F12 → Console tab
3. **System logs**: `research_system.log` file

### Common Log Messages

- ✅ "Research completed successfully" - Everything working
- ⚠️ "ArXiv search failed" - Internet/API issue
- ❌ "Error in research" - System error

### Report Issues

When reporting issues, include:
1. Error message (exact text)
2. Topic you were researching
3. Browser and version
4. Python version (`python --version`)
5. Server logs

## Advanced Troubleshooting

### Reset the System
```bash
# Stop server (Ctrl+C)
# Delete cache
rm -rf data/memory/*
# Restart server
python app_fixed.py
```

### Check Dependencies
```bash
pip list | grep -E "(flask|requests|aiohttp|pydantic)"
```

### Verify Installation
```bash
python -c "from src.research_system import AutonomousResearchSystem; print('OK')"
```

## FAQ

**Q: Can I run this on a different port?**
A: Yes, edit the `port=5000` line in `app_fixed.py`

**Q: Can I access this from another computer?**
A: Yes, use the IP address shown when starting the server

**Q: How do I stop the server?**
A: Press Ctrl+C in the terminal

**Q: Can I run multiple research requests simultaneously?**
A: The system handles one request at a time to avoid conflicts

**Q: How do I update the system?**
A: Pull the latest code and restart the server