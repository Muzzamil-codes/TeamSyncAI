#!/usr/bin/env python3
"""
Quick verification script for backend integration
Tests if all components are properly configured
"""

import os
import sys
from pathlib import Path

def check_environment():
    """Check environment configuration."""
    print("=" * 50)
    print("ENVIRONMENT CHECK")
    print("=" * 50)
    
    # Check .env file
    if not Path(".env").exists():
        print("❌ .env file not found")
        return False
    print("✓ .env file exists")
    
    # Check API key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not configured")
        return False
    print("✓ GOOGLE_API_KEY configured")
    
    return True


def check_imports():
    """Check if all required modules can be imported."""
    print("\n" + "=" * 50)
    print("IMPORT CHECK")
    print("=" * 50)
    
    imports = [
        ("fastapi", "FastAPI"),
        ("langchain_google_genai", "ChatGoogleGenerativeAI"),
        ("langchain_core.prompts", "PromptTemplate"),
        ("app.core", "ChatAnalysisAgent"),
        ("app.core", "get_agent"),
    ]
    
    all_ok = True
    for module, obj in imports:
        try:
            mod = __import__(module, fromlist=[obj])
            getattr(mod, obj)
            print(f"✓ {module}.{obj}")
        except ImportError as e:
            print(f"❌ {module}.{obj} - {str(e)}")
            all_ok = False
    
    return all_ok


def check_core_modules():
    """Check if core modules exist."""
    print("\n" + "=" * 50)
    print("CORE MODULES CHECK")
    print("=" * 50)
    
    files = [
        "app/core/__init__.py",
        "app/core/rag_agent.py",
        "app/core/chat_parser.py",
        "app/routers/llm_agent.py",
        "requirements.txt",
    ]
    
    all_ok = True
    for file in files:
        if Path(file).exists():
            print(f"✓ {file}")
        else:
            print(f"❌ {file} - NOT FOUND")
            all_ok = False
    
    return all_ok


def check_agent_initialization():
    """Test if ChatAnalysisAgent can be initialized."""
    print("\n" + "=" * 50)
    print("AGENT INITIALIZATION CHECK")
    print("=" * 50)
    
    try:
        from app.core import get_agent
        agent = get_agent()
        print(f"✓ ChatAnalysisAgent initialized")
        print(f"  - Model: {agent.model_name}")
        print(f"  - API Key: {'***' + agent.api_key[-4:] if agent.api_key else 'NOT SET'}")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize agent: {str(e)}")
        return False


def main():
    """Run all checks."""
    print("\n")
    print("╔" + "=" * 48 + "╗")
    print("║" + " BACKEND INTEGRATION VERIFICATION ".center(48) + "║")
    print("╚" + "=" * 48 + "╝")
    print()
    
    checks = [
        ("Environment Configuration", check_environment),
        ("Module Imports", check_imports),
        ("Core Files", check_core_modules),
        ("Agent Initialization", check_agent_initialization),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"\n⚠️  {check_name} failed with exception: {str(e)}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    all_passed = all(result for _, result in results)
    
    for check_name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status}: {check_name}")
    
    print()
    if all_passed:
        print("🎉 All checks passed! Backend is ready to use.")
        print()
        print("Start the server with:")
        print("  uvicorn app.main:app --reload --port 8000")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
