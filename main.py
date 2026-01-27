"""
Main entry point for the Autonomous Research Agent System.
"""
import asyncio
import json
from pathlib import Path
from src.research_system import AutonomousResearchSystem


async def main():
    """Main function to run the research system."""
    
    # Initialize the research system
    system = AutonomousResearchSystem()
    
    # Example research topic
    topic = "Use of Graph Neural Networks in Drug Discovery"
    
    print(f"🔬 Starting autonomous research on: {topic}")
    print("=" * 60)
    
    try:
        # Perform research
        results = await system.research(topic)
        
        # Display results
        print("\n📊 RESEARCH RESULTS")
        print("=" * 60)
        
        print(f"\n🎯 Topic Map:")
        print(f"Main Topic: {results.topic_map.main_topic}")
        print(f"Subtopics: {', '.join(results.topic_map.subtopics[:5])}")
        print(f"Methods: {', '.join(results.topic_map.methods[:5])}")
        print(f"Keywords: {', '.join(results.topic_map.keywords[:10])}")
        
        print(f"\n📚 Papers Discovered: {len(results.papers)}")
        for i, paper in enumerate(results.papers[:3], 1):
            print(f"{i}. {paper.title}")
            print(f"   Authors: {', '.join(paper.authors[:3])}")
            print(f"   Year: {paper.year}, Venue: {paper.venue}")
            print(f"   Relevance: {paper.relevance_score:.2f}")
            print()
        
        print(f"\n🔍 Claims Extracted: {len(results.claims)}")
        for i, claim in enumerate(results.claims[:3], 1):
            print(f"{i}. {claim.statement[:100]}...")
            if claim.metrics:
                print(f"   Metrics: {claim.metrics}")
            print(f"   Confidence: {claim.confidence:.2f}")
            print()
        
        print(f"\n⚡ Contradictions Found: {len(results.contradictions)}")
        print(f"🔬 Research Gaps Identified: {len(results.research_gaps)}")
        print(f"📖 Citations Generated: {len(results.citations)}")
        
        # Save results to file
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Save as JSON (simplified version)
        output_data = {
            "topic": results.topic_map.main_topic,
            "generated_at": results.generated_at.isoformat(),
            "summary": {
                "papers_analyzed": results.total_papers_analyzed,
                "claims_extracted": results.total_claims_extracted,
                "contradictions_found": len(results.contradictions),
                "research_gaps_identified": len(results.research_gaps)
            },
            "papers": [
                {
                    "title": paper.title,
                    "authors": paper.authors,
                    "year": paper.year,
                    "venue": paper.venue,
                    "relevance_score": paper.relevance_score
                }
                for paper in results.papers
            ],
            "top_claims": [
                {
                    "statement": claim.statement,
                    "metrics": claim.metrics,
                    "confidence": claim.confidence
                }
                for claim in results.claims[:10]
            ]
        }
        
        with open(output_dir / "research_results.json", "w") as f:
            json.dump(output_data, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {output_dir / 'research_results.json'}")
        
        # Display memory stats
        memory_stats = await system.get_memory_stats()
        print(f"\n🧠 Memory Stats:")
        print(f"Cache size: {memory_stats['cache_size']}")
        print(f"Knowledge nodes: {memory_stats['knowledge_nodes']}")
        print(f"Knowledge edges: {memory_stats['knowledge_edges']}")
        
    except Exception as e:
        print(f"❌ Error during research: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())