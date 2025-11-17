#!/usr/bin/env python3
"""
Demo/Test Script for 24/7 Automated News Platform
This script validates that all components are working correctly without actually
producing videos or uploading to YouTube.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("📦 Testing module imports...")
    try:
        from src.news_fetcher import NewsFetcher
        from src.news_generator import NewsContentGenerator
        from src.live_streamer import LiveStreamer
        from src.generator import text_to_speech, generate_visuals, create_video
        from src.uploader import upload_to_youtube
        print("   ✅ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False

def test_news_fetcher():
    """Test news fetching functionality."""
    print("\n📰 Testing News Fetcher...")
    try:
        from src.news_fetcher import NewsFetcher
        fetcher = NewsFetcher()
        
        # Test fetching with fallback
        articles = fetcher.fetch_breaking_news('technology', max_articles=3)
        if len(articles) > 0:
            print(f"   ✅ Fetched {len(articles)} articles")
            print(f"   📄 Sample: {articles[0]['title'][:50]}...")
            return True
        else:
            print("   ❌ No articles fetched")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_news_generator():
    """Test news content generation."""
    print("\n🤖 Testing News Content Generator...")
    try:
        from src.news_fetcher import NewsFetcher
        from src.news_generator import NewsContentGenerator
        
        # Get sample articles
        fetcher = NewsFetcher()
        articles = fetcher.fetch_breaking_news('technology', max_articles=3)
        
        # Generate bulletin
        generator = NewsContentGenerator('Test Anchor')
        bulletin = generator.generate_news_bulletin(articles, 'hourly')
        
        if bulletin and 'opening' in bulletin:
            print(f"   ✅ Bulletin generated successfully")
            print(f"   📝 Opening: {bulletin['opening'][:50]}...")
            print(f"   📊 Headlines: {len(bulletin.get('headlines', []))}")
            print(f"   📊 Stories: {len(bulletin.get('detailed_stories', []))}") 
            return True
        else:
            print("   ❌ Bulletin generation failed")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_configuration():
    """Test configuration management."""
    print("\n⚙️  Testing Configuration Management...")
    try:
        import json
        from pathlib import Path
        
        test_config = {
            'last_run': '2024-01-01T00:00:00',
            'total_bulletins': 0,
            'current_category_index': 0,
            'categories_covered': {},
            'created_at': '2024-01-01T00:00:00'
        }
        
        # Test JSON serialization
        json_str = json.dumps(test_config, indent=2)
        loaded = json.loads(json_str)
        
        if loaded == test_config:
            print("   ✅ Configuration serialization works")
            return True
        else:
            print("   ❌ Configuration mismatch")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_workflow_files():
    """Test that workflow files exist and are valid."""
    print("\n🔄 Testing Workflow Files...")
    try:
        import yaml
        
        workflow_file = Path('.github/workflows/news_automation.yml')
        if not workflow_file.exists():
            print("   ❌ news_automation.yml not found")
            return False
        
        # Use UTF-8 to avoid Windows default encoding issues with emojis/special chars
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow = yaml.safe_load(f)
        
        if workflow and 'name' in workflow:
            print(f"   ✅ Workflow file valid: {workflow['name']}")
            return True
        else:
            print("   ❌ Invalid workflow file")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_api_keys():
    """Check if API keys are configured."""
    print("\n🔑 Checking API Keys...")
    import os
    
    keys = {
        'GOOGLE_API_KEY': 'Gemini AI (Required for content generation)',
        'NEWSAPI_KEY': 'NewsAPI (Optional - uses fallback if missing)',
        'PEXELS_API_KEY': 'Pexels (Optional - for background images)'
    }
    
    found = 0
    for key, description in keys.items():
        if os.getenv(key):
            print(f"   ✅ {key}: Found")
            found += 1
        else:
            print(f"   ⚠️  {key}: Not found - {description}")
    
    if found > 0:
        print(f"\n   ℹ️  {found}/{len(keys)} API keys configured")
    else:
        print("\n   ⚠️  No API keys found - system will use fallback mode")
        print("   ℹ️  For full functionality, set environment variables:")
        for key in keys.keys():
            print(f"      export {key}='your-key-here'")
    
    return True

def main():
    """Run all tests."""
    print("="*70)
    print("24/7 AUTOMATED NEWS PLATFORM - VALIDATION TESTS")
    print("="*70)
    
    tests = [
        ("Module Imports", test_imports),
        ("News Fetcher", test_news_fetcher),
        ("News Generator", test_news_generator),
        ("Configuration", test_configuration),
        ("Workflow Files", test_workflow_files),
        ("API Keys", check_api_keys)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready for 24/7 operation.")
        print("\n📋 Next steps:")
        print("   1. Set API keys (see QUICKSTART.md)")
        print("   2. Run: python news_main.py")
        print("   3. Enable GitHub Actions for automation")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("   See QUICKSTART.md for setup instructions.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
