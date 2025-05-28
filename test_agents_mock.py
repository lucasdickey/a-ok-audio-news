#!/usr/bin/env python3
"""
Real test for the agents pipeline using actual Anthropic API calls.
"""

import os
import sys
import anthropic

# Import the agents pipeline
import agents_pipeline

def test_api_key():
    """Test if the API key is properly configured."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        return False
    
    try:
        # Test a simple API call
        client = anthropic.Client(api_key=api_key)
        response = client.messages.create(
            model="claude-3-haiku-20240307",  # Use cheaper model for testing
            max_tokens=50,
            messages=[{"role": "user", "content": "Hello, just testing the API connection. Please respond with 'API test successful'."}]
        )
        print("✅ API key is valid and working")
        return True
    except anthropic.AuthenticationError:
        print("❌ API key is invalid or expired")
        return False
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def test_agents_pipeline():
    print("🤖 Testing Agents Pipeline with Real API Calls")
    print("=" * 50)
    
    # First test API connectivity
    if not test_api_key():
        print("\n❌ Cannot proceed with testing - API key issue")
        return None
    
    try:
        print("\n🔬 Testing Full Pipeline (this may take a few minutes)...")
        print("   📅 Date: 2025-05-25")
        print("   🧠 Editor: Enabled")
        print("   👁️ Human Review: Disabled")
        
        episode_result = agents_pipeline.generate_episode(
            date_str="2025-05-25",
            with_editor=True,
            human_review=False
        )
        
        print(f"\n✅ Full pipeline executed successfully!")
        print(f"   📊 Episode data keys: {list(episode_result.keys())}")
        
        # Show some preview of results
        if episode_result.get('research'):
            print(f"   🔍 Research length: {len(episode_result['research'])} characters")
            print(f"   🔍 Research preview: {episode_result['research'][:150]}...")
        
        if episode_result.get('summary'):
            print(f"   📝 Summary length: {len(episode_result['summary'])} characters")
            print(f"   📝 Summary preview: {episode_result['summary'][:150]}...")
            
        if episode_result.get('script'):
            print(f"   🎙️ Script length: {len(episode_result['script'])} characters")
            print(f"   🎙️ Script preview: {episode_result['script'][:200]}...")
        
        print("\n🎉 All tests passed! The agents pipeline is working with real API calls.")
        print("\n📝 Quality check:")
        print("   - Review the generated content above")
        print("   - Check if it follows the sample script format")
        print("   - Verify source citations are included")
        print("   - Ensure AI practitioner focus is maintained")
        
        return episode_result
        
    except Exception as e:
        print(f"\n❌ Pipeline test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return None

if __name__ == "__main__":
    test_result = test_agents_pipeline()
    
    if test_result:
        print(f"\n📄 Full results available in test_result variable")
        print(f"    Keys: {list(test_result.keys())}")
    else:
        print(f"\n❌ Test failed - check API key and try again") 