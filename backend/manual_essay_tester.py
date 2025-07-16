#!/usr/bin/env python3
"""
Manual Essay Testing Script

This script allows you to test real essays with the APUSH Grader backend
and view detailed results for manual evaluation of grading quality.

Usage:
    python manual_essay_tester.py [essay_file] [essay_type] [prompt_file]

Examples:
    python manual_essay_tester.py sample_essays/dbq_essay.txt dbq sample_essays/prompts/dbq_prompt.txt
    python manual_essay_tester.py sample_essays/leq_essay.txt leq sample_essays/prompts/leq_prompt.txt
    python manual_essay_tester.py sample_essays/saq_essay.txt saq sample_essays/prompts/saq_prompt.txt

Or run interactively:
    python manual_essay_tester.py

Quick test with samples:
    python manual_essay_tester.py --sample dbq
    python manual_essay_tester.py --sample leq
    python manual_essay_tester.py --sample saq
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional, Tuple

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.config.settings import Settings
from app.models.core import EssayType, SAQType
from app.utils.grading_workflow import grade_essay_with_validation


def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_results(result, essay_type: EssayType, essay_text: str, prompt: str):
    """Print detailed results in a readable format"""
    
    print_header("📝 ESSAY GRADING RESULTS")
    
    # Basic info
    print(f"Essay Type: {essay_type.value.upper()}")
    print(f"Essay Length: {len(essay_text.split())} words")
    print(f"Prompt: {prompt[:100]}..." if len(prompt) > 100 else f"Prompt: {prompt}")
    
    # Score information
    percentage_display = ""
    if hasattr(result, 'percentage_score'):
        percentage_display = f" ({result.percentage_score:.1f}%)"
    elif hasattr(result, 'percentage'):
        percentage_display = f" ({result.percentage:.1f}%)"
    
    print(f"\n🎯 SCORE: {result.score}/{result.max_score}{percentage_display}")
    
    # Letter grade and performance level if available
    if hasattr(result, 'letter_grade') and hasattr(result, 'performance_level'):
        print(f"   Letter Grade: {result.letter_grade} ({result.performance_level})")
    
    # Word and paragraph count if available
    if hasattr(result, 'word_count') and result.word_count:
        print(f"   Word Count: {result.word_count}")
    if hasattr(result, 'paragraph_count') and result.paragraph_count:
        print(f"   Paragraph Count: {result.paragraph_count}")
    
    # Breakdown
    print(f"\n📊 BREAKDOWN:")
    if hasattr(result.breakdown, '__dict__'):
        # Handle SAQBreakdown and DBQLeqBreakdown objects
        for field_name, rubric_item in result.breakdown.__dict__.items():
            if hasattr(rubric_item, 'score'):
                percentage = (rubric_item.score / rubric_item.max_score) * 100
                print(f"   {field_name}: {rubric_item.score}/{rubric_item.max_score} ({percentage:.1f}%)")
                print(f"     └─ {rubric_item.feedback}")
    elif isinstance(result.breakdown, dict):
        for category, details in result.breakdown.items():
            if isinstance(details, dict):
                score = details.get('score', 'N/A')
                feedback = details.get('feedback', 'No feedback')
                print(f"   {category}: {score}")
                print(f"     └─ {feedback}")
            else:
                print(f"   {category}: {details}")
    else:
        print(f"   {result.breakdown}")
    
    # Overall feedback
    print(f"\n💬 OVERALL FEEDBACK:")
    feedback_lines = result.overall_feedback.split('\n')
    for line in feedback_lines:
        if line.strip():
            print(f"   {line.strip()}")
    
    # Suggestions
    print(f"\n💡 SUGGESTIONS:")
    if isinstance(result.suggestions, list):
        for i, suggestion in enumerate(result.suggestions, 1):
            print(f"   {i}. {suggestion}")
    else:
        print(f"   {result.suggestions}")
    
    print(f"\n{'='*60}")


def load_file(file_path: str) -> Optional[str]:
    """Load content from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None
    except Exception as e:
        print(f"❌ Error reading file {file_path}: {e}")
        return None


def get_essay_type(type_str: str) -> Optional[EssayType]:
    """Convert string to EssayType enum"""
    type_map = {
        'dbq': EssayType.DBQ,
        'leq': EssayType.LEQ,
        'saq': EssayType.SAQ,
    }
    return type_map.get(type_str.lower())


def get_saq_type(type_str: str) -> Optional[SAQType]:
    """Convert string to SAQType enum"""
    type_map = {
        'stimulus': SAQType.STIMULUS,
        'non_stimulus': SAQType.NON_STIMULUS,
        'non-stimulus': SAQType.NON_STIMULUS,
        'secondary_comparison': SAQType.SECONDARY_COMPARISON,
        'secondary-comparison': SAQType.SECONDARY_COMPARISON,
        'comparison': SAQType.SECONDARY_COMPARISON,
    }
    return type_map.get(type_str.lower())


def sample_mode(essay_type_str: str, saq_type_str: str = None) -> Optional[Tuple[str, EssayType, str, SAQType]]:
    """Run with sample essays"""
    essay_type = get_essay_type(essay_type_str)
    if not essay_type:
        print(f"❌ Invalid essay type: {essay_type_str}. Use DBQ, LEQ, or SAQ")
        return None
    
    saq_type = None
    if essay_type == EssayType.SAQ and saq_type_str:
        saq_type = get_saq_type(saq_type_str)
        if not saq_type:
            print(f"❌ Invalid SAQ type: {saq_type_str}. Use stimulus, non_stimulus, or secondary_comparison")
            return None
    
    # Load sample files
    if essay_type == EssayType.SAQ and saq_type:
        essay_file = f"sample_essays/saq_{saq_type.value}_essay.txt"
        prompt_file = f"sample_essays/prompts/saq_{saq_type.value}_prompt.txt"
    else:
        essay_file = f"sample_essays/{essay_type_str.lower()}_essay.txt"
        prompt_file = f"sample_essays/prompts/{essay_type_str.lower()}_prompt.txt"
    
    essay_text = load_file(essay_file)
    if not essay_text:
        return None
    
    prompt = load_file(prompt_file)
    if not prompt:
        return None
    
    type_display = f"{essay_type_str.upper()}"
    if saq_type:
        type_display += f" ({saq_type.display_name})"
    
    print(f"✅ Loaded sample {type_display} essay and prompt")
    return essay_text, essay_type, prompt, saq_type


def interactive_mode() -> Optional[Tuple[str, EssayType, str]]:
    """Run in interactive mode"""
    print_header("🎓 APUSH Grader - Manual Essay Tester")
    print("Interactive Mode - Enter essay details manually")
    
    # Get essay type
    print("\nAvailable essay types: DBQ, LEQ, SAQ")
    essay_type_str = input("Enter essay type: ").strip()
    essay_type = get_essay_type(essay_type_str)
    
    if not essay_type:
        print("❌ Invalid essay type. Use DBQ, LEQ, or SAQ")
        return None
    
    # Get prompt
    print(f"\nEnter the {essay_type.value.upper()} prompt:")
    prompt = input("Prompt: ").strip()
    
    if not prompt:
        print("❌ Prompt cannot be empty")
        return None
    
    # Get essay text
    print(f"\nEnter the {essay_type.value.upper()} essay (press Enter twice to finish):")
    essay_lines = []
    empty_count = 0
    
    while True:
        line = input()
        if line == "":
            empty_count += 1
            if empty_count >= 2:
                break
        else:
            empty_count = 0
            essay_lines.append(line)
    
    essay_text = "\n".join(essay_lines).strip()
    
    if not essay_text:
        print("❌ Essay cannot be empty")
        return None
    
    return essay_text, essay_type, prompt


def file_mode(essay_file: str, essay_type_str: str, prompt_file: str) -> Optional[Tuple[str, EssayType, str]]:
    """Run in file mode"""
    print_header("🎓 APUSH Grader - Manual Essay Tester")
    print("File Mode - Loading from files")
    
    # Load essay
    essay_text = load_file(essay_file)
    if not essay_text:
        return None
    
    # Get essay type
    essay_type = get_essay_type(essay_type_str)
    if not essay_type:
        print(f"❌ Invalid essay type: {essay_type_str}. Use DBQ, LEQ, or SAQ")
        return None
    
    # Load prompt
    prompt = load_file(prompt_file)
    if not prompt:
        return None
    
    print(f"✅ Loaded {essay_type_str.upper()} essay from {essay_file}")
    print(f"✅ Loaded prompt from {prompt_file}")
    
    return essay_text, essay_type, prompt


def print_usage():
    """Print usage information"""
    print("Usage:")
    print("  python manual_essay_tester.py [essay_file] [essay_type] [prompt_file]")
    print("  python manual_essay_tester.py --sample [dbq|leq|saq]")
    print("  python manual_essay_tester.py --sample saq [stimulus|non_stimulus|secondary_comparison]")
    print("  python manual_essay_tester.py  (interactive mode)")
    print("\nExamples:")
    print("  python manual_essay_tester.py sample_essays/dbq_essay.txt dbq sample_essays/prompts/dbq_prompt.txt")
    print("  python manual_essay_tester.py --sample dbq")
    print("  python manual_essay_tester.py --sample saq stimulus")
    print("  python manual_essay_tester.py")


async def main():
    """Main function"""
    
    # Check if API key is set
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or not api_key.startswith("sk-"):
        print("⚠️  ANTHROPIC_API_KEY environment variable not set or invalid")
        print("   Set it to use real AI grading:")
        print("   export ANTHROPIC_API_KEY='sk-ant-api03-your-key-here'")
        print("   \nUsing mock AI for testing...")
        ai_service_type = "mock"
    else:
        ai_service_type = "anthropic"
        print(f"✅ Using real Anthropic API (Key: {api_key[:20]}...)")
    
    # Set environment
    os.environ["AI_SERVICE_TYPE"] = ai_service_type
    if ai_service_type == "anthropic":
        os.environ["ANTHROPIC_API_KEY"] = api_key
    
    # Parse arguments
    if len(sys.argv) == 1:
        # Interactive mode
        result = interactive_mode()
        if result:
            essay_text, essay_type, prompt = result
            saq_type = None
    elif len(sys.argv) == 3 and sys.argv[1] == "--sample":
        # Sample mode
        essay_type_str = sys.argv[2]
        result = sample_mode(essay_type_str)
        if result:
            essay_text, essay_type, prompt, saq_type = result
    elif len(sys.argv) == 4 and sys.argv[1] == "--sample":
        # Sample mode with SAQ type
        essay_type_str = sys.argv[2]
        saq_type_str = sys.argv[3]
        result = sample_mode(essay_type_str, saq_type_str)
        if result:
            essay_text, essay_type, prompt, saq_type = result
    elif len(sys.argv) == 4:
        # File mode
        essay_file, essay_type_str, prompt_file = sys.argv[1], sys.argv[2], sys.argv[3]
        result = file_mode(essay_file, essay_type_str, prompt_file)
        if result:
            essay_text, essay_type, prompt = result
            saq_type = None
    else:
        print_usage()
        return
    
    if not result:
        return
    
    # Grade the essay
    type_display = f"{essay_type.value.upper()}"
    if saq_type:
        type_display += f" ({saq_type.display_name})"
    
    print(f"\n🔄 Grading {type_display} essay...")
    print(f"   Service: {ai_service_type.upper()}")
    print(f"   Essay length: {len(essay_text.split())} words")
    
    try:
        grade_result = await grade_essay_with_validation(
            essay_text=essay_text,
            essay_type=essay_type,
            prompt=prompt,
            saq_type=saq_type
        )
        
        # Display results
        print_results(grade_result, essay_type, essay_text, prompt)
        
        # Success message
        print(f"\n🎉 Grading completed successfully!")
        if ai_service_type == "anthropic":
            print(f"   Cost: ~$0.02-0.03 for this essay")
        
    except Exception as e:
        print(f"❌ Error grading essay: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())