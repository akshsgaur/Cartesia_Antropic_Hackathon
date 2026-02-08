#!/usr/bin/env python3
"""
Get available Cartesia voices and their IDs
"""

import requests
import json
import os

def get_cartesia_voices():
    """Fetch available voices from Cartesia API"""
    
    api_key = os.getenv("CARTESIA_API_KEY")
    if not api_key:
        print("❌ Error: CARTESIA_API_KEY not found in environment")
        return
    
    url = "https://api.cartesia.ai/voices"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Cartesia-Version": "2025-04-16"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        voices = response.json()["data"]
        
        print("🎤 Available Cartesia Voices:")
        print("=" * 80)
        
        # Group by language
        by_language = {}
        for voice in voices:
            lang = voice.get("language", "unknown")
            if lang not in by_language:
                by_language[lang] = []
            by_language[lang].append(voice)
        
        # Display voices by language
        for lang, lang_voices in sorted(by_language.items()):
            print(f"\n🌍 {lang.upper()} Voices:")
            print("-" * 40)
            
            for voice in lang_voices:
                voice_id = voice.get("id", "N/A")
                name = voice.get("name", "Unnamed")
                description = voice.get("description", "")
                is_public = "✅ Public" if voice.get("is_public") else "🔒 Private"
                
                print(f"  🎭 {name}")
                print(f"     ID: {voice_id}")
                print(f"     {is_public}")
                if description:
                    print(f"     📝 {description}")
                print()
        
        # Recommended voices for voice agents
        print("\n🎯 Recommended for Voice Agents:")
        print("-" * 40)
        
        recommended_ids = [
            "f786b574-daa5-4673-aa0c-cbe3e8534c02",  # Katie
            "228fca29-3a0a-435c-8728-5cb483251068",  # Kiefer
        ]
        
        for voice in voices:
            if voice.get("id") in recommended_ids:
                name = voice.get("name", "Unnamed")
                voice_id = voice.get("id")
                print(f"  ⭐ {name} - ID: {voice_id}")
        
        # Emotive voices for expressive characters
        print("\n🎭 Emotive Voices (for expressive characters):")
        print("-" * 40)
        
        emotive_ids = [
            "6ccbfb76-1fc6-48f7-b71d-91ac6298247b",  # Tessa
            "c961b81c-a935-4c17-bfb3-ba2239de8c2f",  # Kyle
        ]
        
        for voice in voices:
            if voice.get("id") in emotive_ids:
                name = voice.get("name", "Unnamed")
                voice_id = voice.get("id")
                print(f"  🎨 {name} - ID: {voice_id}")
        
        print(f"\n📊 Total voices available: {len(voices)}")
        
        return voices
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching voices: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing response: {e}")
        return None

if __name__ == "__main__":
    get_cartesia_voices()
