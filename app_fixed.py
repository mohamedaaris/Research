"""
Flask web frontend for the Autonomous Research Agent System - Fixed version.
"""
from flask import Flask, render_template, request, jsonify, send_file
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import threading
import concurrent.futures

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.research_system import AutonomousResearchSystem
from src.agents.custom_citation_formatter import CustomCitationFormatter

app = Flask(__name__)
app.config['SECRET_KEY'] = 'research-system-secret-key'

# Global system instance
research_system = None
executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

def get_system():
    """Get or create research system instance."""
    global research_system
    if research_system is None:
        research_system = AutonomousResearchSystem()
    return research_system


def run_research_in_thread(topic):
    """Run research in a separate thread with its own event loop."""
    def research_task():
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            system = get_system()
            result = loop.run_until_complete(system.research(topic))
            return result
        except Exception as e:
            raise e
        finally:
            loop.close()
    
    return research_task()


def _generate_custom_citation(paper):
    """Generate custom citation format."""
    # Generate bibitem key
    bibitem_key = _generate_bibitem_key(paper)
    
    # Format authors
    formatted_authors = _format_authors_custom(paper.authors)
    
    # Format title
    formatted_title = _format_title_custom(paper.title)
    
    # Get paper URL
    paper_url = _get_paper_url(paper)
    
    # Create citation
    citation = f"\\bibitem{{{bibitem_key}}} {formatted_authors}, {formatted_title}, {paper.venue} \\textbf{{1}}(1) ({paper.year}) 1--10"
    
    if paper_url:
        citation += f". {paper_url}"
    
    return citation


def _generate_bibitem_key(paper):
    """Generate bibitem key from authors and year."""
    if not paper.authors:
        return f"Unknown{paper.year % 100:02d}"
    
    # Get first 2-3 authors
    authors_for_key = paper.authors[:3] if len(paper.authors) >= 3 else paper.authors[:2]
    
    # Extract first two letters of last names
    key_parts = []
    for author in authors_for_key:
        last_name = author.split()[-1] if author.split() else author
        if len(last_name) >= 2:
            key_parts.append(last_name[:2].title())
        elif len(last_name) == 1:
            key_parts.append(last_name.upper())
    
    # Add year (last 2 digits)
    year_suffix = paper.year % 100
    
    key = "".join(key_parts) + f"{year_suffix:02d}"
    return key


def _format_authors_custom(authors):
    """Format authors with initials first, then last name."""
    if not authors:
        return "Unknown Author"
    
    formatted_authors = []
    
    for author in authors:
        author = author.strip()
        parts = author.split()
        
        if len(parts) < 2:
            formatted_authors.append(author)
            continue
        
        # Check if author is already in correct format (e.g., "Y. Saad", "M.H. Schultz")
        if len(parts) == 2 and len(parts[0]) <= 4 and '.' in parts[0]:
            # Already in format like "Y. Saad" or "M.H. Schultz"
            formatted_authors.append(author)
            continue
            
        # Last part is last name
        last_name = parts[-1]
        
        # Everything else is first/middle names
        first_middle = parts[:-1]
        
        # Create initials
        initials = []
        for name in first_middle:
            if name and name[0].isalpha():
                # Handle names that might already have periods
                if name.endswith('.'):
                    initials.append(name)
                else:
                    initials.append(f"{name[0].upper()}.")
        
        # Format as "F.M. Last" (initials first, then last name)
        if initials:
            formatted_authors.append(f"{''.join(initials)} {last_name}")
        else:
            formatted_authors.append(last_name)
    
    return ", ".join(formatted_authors)


def _format_title_custom(title):
    """Format title with only first letter capital, except proper nouns."""
    if not title:
        return ""
    
    # Clean title
    title = title.strip()
    if title.endswith('.'):
        title = title[:-1]
    
    # Convert to lowercase first
    title_lower = title.lower()
    
    # Capitalize first letter
    if title_lower:
        title_formatted = title_lower[0].upper() + title_lower[1:]
    else:
        title_formatted = title_lower
    
    # Capitalize proper nouns
    proper_nouns = ["wiener", "euler", "hamilton", "fibonacci", "pascal", "newton", "gauss",
                   "fourier", "laplace", "bayes", "markov", "poisson", "bernoulli",
                   "covid", "sars", "hiv", "aids", "dna", "rna", "pcr", "crispr"]
    
    for proper_noun in proper_nouns:
        import re
        pattern = r'\b' + re.escape(proper_noun.lower()) + r'\b'
        replacement = proper_noun.capitalize()
        title_formatted = re.sub(pattern, replacement, title_formatted, flags=re.IGNORECASE)
    
    return title_formatted


def _get_paper_url(paper):
    """Get the best URL for the paper."""
    if paper.doi:
        if paper.doi.startswith('http'):
            return paper.doi
        else:
            return f"https://doi.org/{paper.doi}"
    elif paper.url:
        return paper.url
    elif paper.arxiv_id:
        return f"https://arxiv.org/abs/{paper.arxiv_id}"
    else:
        return ""


@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')


@app.route('/research', methods=['POST'])
def research():
    """Perform research on a topic."""
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        print(f"Starting research on topic: {topic}")
        
        # Run research in a separate thread to avoid event loop conflicts
        future = executor.submit(run_research_in_thread, topic)
        results = future.result(timeout=300)  # 5 minute timeout
        
        print(f"Research completed successfully")
        
        # Convert results to JSON-serializable format
        response_data = {
            'topic': results.topic_map.main_topic,
            'generated_at': results.generated_at.isoformat(),
            'summary': {
                'papers_analyzed': results.total_papers_analyzed,
                'claims_extracted': results.total_claims_extracted,
                'contradictions_found': len(results.contradictions),
                'research_gaps_identified': len(results.research_gaps)
            },
            'topic_map': {
                'main_topic': results.topic_map.main_topic,
                'subtopics': results.topic_map.subtopics,
                'methods': results.topic_map.methods,
                'keywords': results.topic_map.keywords,
                'datasets': results.topic_map.datasets
            },
            'papers': [
                {
                    'title': paper.title,
                    'authors': paper.authors,
                    'year': paper.year,
                    'venue': paper.venue,
                    'relevance_score': paper.relevance_score,
                    'abstract': paper.abstract[:300] + '...' if len(paper.abstract) > 300 else paper.abstract,
                    'doi': paper.doi,
                    'arxiv_id': paper.arxiv_id,
                    'url': paper.url
                }
                for paper in results.papers
            ],
            'claims': [
                {
                    'statement': claim.statement,
                    'confidence': claim.confidence,
                    'metrics': claim.metrics,
                    'datasets': claim.datasets,
                    'conditions': claim.conditions
                }
                for claim in results.claims
            ],
            'contradictions': [
                {
                    'explanation': contradiction.explanation,
                    'type': contradiction.contradiction_type,
                    'severity': contradiction.severity
                }
                for contradiction in results.contradictions
            ],
            'research_gaps': [
                {
                    'description': gap.description,
                    'type': gap.gap_type,
                    'priority': gap.priority,
                    'potential_questions': gap.potential_questions
                }
                for gap in results.research_gaps
            ],
            'citations': [
                {
                    'paper_id': citation.paper_id,
                    'bibtex': citation.bibtex,
                    'apa': citation.apa,
                    'ieee': citation.ieee,
                    'mla': citation.mla if hasattr(citation, 'mla') else None,
                    'custom_format': _generate_custom_citation(paper),
                    'paper_url': _get_paper_url(paper),
                    'journal_name': paper.venue,
                    'year': paper.year
                }
                for citation, paper in zip(results.citations, results.papers)
            ]
        }
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"research_{timestamp}.json"
        filepath = Path("output") / filename
        
        with open(filepath, 'w') as f:
            json.dump(response_data, f, indent=2, default=str)
        
        response_data['download_url'] = f'/download/{filename}'
        
        return jsonify(response_data)
        
    except concurrent.futures.TimeoutError:
        return jsonify({'error': 'Research timed out. Please try a more specific topic.'}), 500
    except Exception as e:
        print(f"Error in research: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Research failed: {str(e)}'}), 500


@app.route('/download/<filename>')
def download_file(filename):
    """Download research results file."""
    try:
        filepath = Path("output") / filename
        if filepath.exists():
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/history')
def history():
    """Get list of previous research results."""
    try:
        output_dir = Path("output")
        files = []
        
        if output_dir.exists():
            for file in output_dir.glob("research_*.json"):
                try:
                    with open(file, 'r') as f:
                        data = json.load(f)
                    
                    files.append({
                        'filename': file.name,
                        'topic': data.get('topic', 'Unknown'),
                        'generated_at': data.get('generated_at', ''),
                        'papers_count': len(data.get('papers', [])),
                        'claims_count': len(data.get('claims', [])),
                        'download_url': f'/download/{file.name}'
                    })
                except:
                    continue
        
        # Sort by date (newest first)
        files.sort(key=lambda x: x['generated_at'], reverse=True)
        
        return jsonify(files)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/citations')
def citations_page():
    """Enhanced citations page."""
    return render_template('enhanced_citations.html')


@app.route('/generate-custom-citations', methods=['POST'])
def generate_custom_citations():
    """Generate custom formatted citations."""
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        print(f"Generating custom citations for topic: {topic}")
        
        # Run research and citation generation in a separate thread
        future = executor.submit(run_citation_generation, topic)
        results = future.result(timeout=300)  # 5 minute timeout
        
        print(f"Custom citations generated successfully")
        
        return jsonify(results)
        
    except concurrent.futures.TimeoutError:
        return jsonify({'error': 'Citation generation timed out. Please try a more specific topic.'}), 500
    except Exception as e:
        print(f"Error in citation generation: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Citation generation failed: {str(e)}'}), 500


def run_citation_generation(topic):
    """Run citation generation in a separate thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Get research system and run research
        system = get_system()
        results = loop.run_until_complete(system.research(topic))
        
        # Generate custom citations
        formatter = CustomCitationFormatter()
        custom_citations = loop.run_until_complete(formatter.process(results.papers))
        
        # Get statistics
        stats = formatter.get_citation_stats(custom_citations)
        
        return {
            'topic': topic,
            'citations': custom_citations,
            'stats': stats,
            'total_papers': len(results.papers)
        }
        
    finally:
        loop.close()
    """Test endpoint to verify the system works."""
    try:
        system = get_system()
        return jsonify({
            'status': 'ok',
            'message': 'Research system is ready',
            'system_initialized': system is not None
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    # Create output directory
    Path("output").mkdir(exist_ok=True)
    
    print("🌐 Starting Research System Web Interface (Fixed Version)")
    print("📍 Open your browser to: http://localhost:5000")
    print("🧪 Test endpoint: http://localhost:5000/test")
    print("📖 Citations page: http://localhost:5000/citations")
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)


def run_citation_generation(topic):
    """Run citation generation in a separate thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Get research system and run research
        system = get_system()
        results = loop.run_until_complete(system.research(topic))
        
        # Generate custom citations
        formatter = CustomCitationFormatter()
        custom_citations = loop.run_until_complete(formatter.process(results.papers))
        
        # Get statistics
        stats = formatter.get_citation_stats(custom_citations)
        
        return {
            'topic': topic,
            'citations': custom_citations,
            'stats': stats,
            'total_papers': len(results.papers)
        }
        
    finally:
        loop.close()