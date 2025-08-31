#!/usr/bin/env python3
"""
Test script to show random meme text combinations
"""

import random

def show_meme_examples(username="User"):
    """Show examples of random meme texts"""
    
    # Collection of funny code and music-related meme texts
    meme_texts = [
        # Code-related memes
        (f"{username} thinks", "they're a data scientist..."),
        (f"{username} when", "the code finally compiles"),
        (f"{username} debugging", "at 3 AM"),
        (f"{username} trying to", "understand their own code"),
        (f"{username} after", "fixing one bug"),
        (f"{username} when", "git merge works"),
        (f"{username} coding", "without Stack Overflow"),
        (f"{username} explaining", "their code to others"),
        (f"{username} trying to", "deploy to production"),
        (f"{username} when", "the tests pass"),
        
        # Music-related memes
        (f"{username} listening to", "their own playlist"),
        (f"{username} when", "their favorite song comes on"),
        (f"{username} trying to", "find the perfect song"),
        (f"{username} analyzing", "music like a pro"),
        (f"{username} discovering", "new music"),
        (f"{username} when", "Spotify recommends hits"),
        (f"{username} explaining", "music theory"),
        (f"{username} trying to", "match the beat"),
        (f"{username} when", "the bass drops"),
        (f"{username} analyzing", "song emotions"),
        
        # Code + Music crossover memes
        (f"{username} coding", "to music"),
        (f"{username} when", "music helps debug"),
        (f"{username} trying to", "code and listen"),
        (f"{username} explaining", "code with music analogies"),
        (f"{username} debugging", "with headphones on"),
        (f"{username} when", "music inspires code"),
        (f"{username} coding", "like a DJ"),
        (f"{username} trying to", "sync code and music"),
        (f"{username} when", "the algorithm grooves"),
        (f"{username} analyzing", "code like a song")
    ]
    
    print(f"🎵 Random Meme Examples for '{username}':\n")
    
    # Show 10 random examples
    for i in range(10):
        text0, text1 = random.choice(meme_texts)
        print(f"{i+1:2d}. {text0}")
        print(f"    {text1}")
        print()
    
    print("✨ Each time you visit the Dashboard, you'll get a different random meme!")

if __name__ == "__main__":
    # Test with different usernames
    print("=" * 50)
    show_meme_examples("Alice")
    
    print("=" * 50)
    show_meme_examples("Bob")
    
    print("=" * 50)
    show_meme_examples("CodeMaster")
