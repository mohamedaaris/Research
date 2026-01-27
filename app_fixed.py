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
                    'mla': citation.mla
                }
                for citation in results.citations
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


@app.route('/test')
def test():
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
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)