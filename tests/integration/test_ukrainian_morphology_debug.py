#!/usr/bin/env python3
"""
Debug test for Ukrainian morphology.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from ai_service.services.ukrainian_morphology import UkrainianMorphologyAnalyzer


def test_ukrainian_morphology():
    """Test Ukrainian morphology for name normalization."""
    analyzer = UkrainianMorphologyAnalyzer()
    
    test_cases = [
        "Сергея",      # Should become "Сергей"
        "Владимировича",  # Should become "Владимирович"
        "Петрова",     # Should become "Петров"
        "Петра",       # Should become "Петр"
    ]
    
    print("🔍 Ukrainian Morphology Debug Test")
    print("=" * 50)
    
    for name in test_cases:
        print(f"Input: '{name}'")
        try:
            forms = analyzer.get_word_forms(name)
            print(f"Forms: {forms}")
            
            # Check if nominative form is present
            nominative_found = any(form.endswith(('ей', 'ов', 'р')) for form in forms)
            print(f"Has nominative form: {'✅' if nominative_found else '❌'}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 30)
    
    print("Test completed!")


if __name__ == "__main__":
    test_ukrainian_morphology()
