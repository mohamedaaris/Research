# 🔑 API Setup Guide: Access All Major Publishers

## 🎯 Goal
Expand your research system to search **Elsevier, Springer, Wiley, and other major publishers** instead of just ArXiv.

## 📊 Current vs Enhanced Coverage

### Currently (ArXiv Only):
- ❌ Limited to preprints and some conference papers
- ❌ Missing published journal articles
- ❌ No access to major publishers

### With Enhanced System:
- ✅ **ArXiv**: Preprints and conference papers
- ✅ **Semantic Scholar**: 200M+ papers from all publishers
- ✅ **CrossRef**: Metadata for 130M+ publications
- ✅ **PubMed**: Life sciences and biomedical literature
- ✅ **Springer Nature**: 13M+ articles and books
- ✅ **Elsevier**: ScienceDirect with 16M+ articles
- ✅ **Wiley**: 1.6M+ articles from Wiley journals

## 🚀 Quick Start (Free APIs)

### 1. Enable Free Sources (No API Key Needed)
```python
# Already working in enhanced system:
- ArXiv ✅
- Semantic Scholar ✅ (optional key for higher limits)
- CrossRef ✅
- PubMed ✅
```

### 2. Test Enhanced Discovery
```bash
python test_enhanced_discovery.py
```

## 🔐 Premium APIs (Require Keys)

### 1. Semantic Scholar (Recommended - Free)
- **What**: 200M+ papers from all major publishers
- **Cost**: Free (optional API key for higher rate limits)
- **Setup**: 
  1. Visit: https://www.semanticscholar.org/product/api
  2. Sign up for free API key
  3. Set: `export SEMANTIC_SCHOLAR_API_KEY='your-key'`

### 2. Springer Nature API
- **What**: Access to Nature, Science, Springer journals
- **Cost**: Free tier (5,000 requests/day)
- **Setup**:
  1. Visit: https://dev.springernature.com/
  2. Create account and get API key
  3. Set: `export SPRINGER_API_KEY='your-key'`
  4. Enable in `api_config.py`: `SPRINGER_ENABLED = True`

### 3. Elsevier ScienceDirect API
- **What**: 16M+ articles from Elsevier journals
- **Cost**: Free tier available, institutional access recommended
- **Setup**:
  1. Visit: https://dev.elsevier.com/
  2. Create account and get API key
  3. Set: `export ELSEVIER_API_KEY='your-key'`
  4. Enable in `api_config.py`: `ELSEVIER_ENABLED = True`

### 4. Wiley API
- **What**: Access to Wiley Online Library
- **Cost**: Often requires institutional access
- **Setup**:
  1. Visit: https://onlinelibrary.wiley.com/library-info/resources/text-and-datamining
  2. Contact your institution or Wiley for access
  3. Set: `export WILEY_API_KEY='your-key'`
  4. Enable in `api_config.py`: `WILEY_ENABLED = True`

## ⚙️ Step-by-Step Setup

### Step 1: Get API Keys
```bash
# Check current setup
python api_config.py

# This shows you which APIs are available and how to get keys
```

### Step 2: Set Environment Variables
```bash
# On Windows (PowerShell)
$env:SPRINGER_API_KEY="your-springer-key-here"
$env:ELSEVIER_API_KEY="your-elsevier-key-here"

# On Linux/Mac
export SPRINGER_API_KEY="your-springer-key-here"
export ELSEVIER_API_KEY="your-elsevier-key-here"
```

### Step 3: Update Configuration
Edit `api_config.py`:
```python
# Enable APIs after getting keys
SPRINGER_ENABLED = True  # After getting Springer key
ELSEVIER_ENABLED = True  # After getting Elsevier key
WILEY_ENABLED = True     # After getting Wiley key

# Set your contact email (required for CrossRef)
CONTACT_EMAIL = "your-real-email@university.edu"
```

### Step 4: Update Research System
Replace the paper discovery agent in `src/research_system.py`:
```python
# Change this line:
from .agents.paper_discovery_agent import PaperDiscoveryAgent

# To this:
from .agents.enhanced_paper_discovery_agent import EnhancedPaperDiscoveryAgent as PaperDiscoveryAgent
```

### Step 5: Test Enhanced System
```bash
python test_enhanced_discovery.py
```

## 📈 Expected Results

### Before (ArXiv only):
```
Papers found: 3-5
Sources: ArXiv only
Coverage: Limited to preprints
```

### After (All sources):
```
Papers found: 50-200
Sources: ArXiv, Semantic Scholar, CrossRef, PubMed, Springer, Elsevier, Wiley
Coverage: Complete academic literature
```

## 💰 Cost Breakdown

### Free Tier (Recommended Start):
- **ArXiv**: Free ✅
- **Semantic Scholar**: Free ✅
- **CrossRef**: Free ✅
- **PubMed**: Free ✅
- **Springer**: 5,000 requests/day free ✅

**Total Cost**: $0/month for substantial coverage

### Premium Tier:
- **Elsevier**: $500-2000/year (institutional)
- **Wiley**: Varies by institution
- **Springer**: Higher limits available

## 🎯 Recommended Setup Strategy

### Phase 1: Free APIs (Start Here)
1. Enable Semantic Scholar (free key)
2. Test with CrossRef and PubMed
3. Add Springer free tier
4. **Result**: 10x more papers than ArXiv alone

### Phase 2: Institutional Access
1. Check if your university has API access
2. Contact library for Elsevier/Wiley access
3. Use institutional credentials
4. **Result**: Complete academic coverage

### Phase 3: Premium (If Needed)
1. Evaluate usage and needs
2. Consider paid plans for high-volume use
3. **Result**: Unlimited access to all publishers

## 🔧 Integration with Web Interface

The enhanced system works seamlessly with your existing web interface:

1. **No UI changes needed** - same interface
2. **More papers found** - better search results
3. **Better citations** - from all major publishers
4. **Improved research gaps** - more comprehensive analysis

## 🚨 Important Notes

### Rate Limits
- **Free APIs**: Respect rate limits (usually 1-10 requests/second)
- **Paid APIs**: Higher limits but still be respectful
- **System handles**: Automatic rate limiting and retries

### Legal Compliance
- **Terms of Service**: Always follow API terms
- **Fair Use**: Don't abuse free tiers
- **Attribution**: Cite sources appropriately

### Institutional Access
- **University VPN**: May be required for some APIs
- **Library Access**: Often provides better API limits
- **Contact Librarian**: They can help with publisher access

## 🧪 Testing Your Setup

### Quick Test
```bash
python test_enhanced_discovery.py
```

### Expected Output
```
📊 Current API Configuration:
  ✅ ArXiv
  ✅ Semantic Scholar
  ✅ CrossRef
  ✅ PubMed
  ✅ Springer Nature
  ✅ Elsevier ScienceDirect

🎯 Total Sources Enabled: 6

📊 RESULTS:
Total papers found: 127

📚 Papers by Source:
  Semantic Scholar: 45 papers
  Springer: 32 papers
  Elsevier: 28 papers
  ArXiv: 15 papers
  CrossRef: 7 papers
```

## 🆘 Troubleshooting

### Common Issues

1. **"API key invalid"**
   - Check key is correct
   - Verify account is active
   - Check rate limits

2. **"No papers found"**
   - Try broader search terms
   - Check internet connection
   - Verify API endpoints

3. **"Rate limit exceeded"**
   - Wait and retry
   - Get API key for higher limits
   - Reduce concurrent requests

### Getting Help

1. **Check logs**: Look for specific error messages
2. **Test individual APIs**: Use test script
3. **Contact support**: Each API provider has support
4. **University library**: Can help with institutional access

## 🎉 Success!

Once set up, your research system will:
- **Find 10-50x more papers** than ArXiv alone
- **Cover all major publishers** (Elsevier, Springer, Wiley, etc.)
- **Generate better citations** from authoritative sources
- **Identify more research gaps** with comprehensive coverage
- **Provide professional-quality results** for any research topic

The enhanced system transforms your research tool from a simple ArXiv searcher into a **comprehensive academic research platform**!