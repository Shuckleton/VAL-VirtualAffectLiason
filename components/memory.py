import json
import os
# Memory setup
memory_file = "val_memory.json"

if os.path.exists(memory_file):
    with open(memory_file, "r") as f:
        memory = json.load(f)
else:
    memory = {
        "user_name": None,
        "favorite_food": None,
        "likes": [],
        "dislikes": [],
        "inside_jokes": [],
        "mode": "normal",
        "emotion": "happy",
        "user_emotion": None,
        "asked_about_val": False
    }

def save_memory():
    with open(memory_file, "w") as f:
        json.dump(memory, f)

def detect_emotion(user_input):
    # Preprocess input once
    lowered = user_input.lower()

    # List of common game references to avoid misinterpretation
    game_references = {"angry birds", "flappy bird", "pacman", "super mario", "tetris"}

    if any(game in lowered for game in game_references):
        return None  # Ignore emotion detection for game references

    # Optimized emotion keyword detection
    emotion_keywords = {
        "happy": {"happy", "joyful", "excited", "grateful", "great", "wonderful"},
        "sad": {"sad", "down", "depressed", "lonely", "blue", "tired"},
        "angry": {"angry", "mad", "furious", "annoyed", "pissed"},
        "anxious": {"anxious", "nervous", "scared", "worried", "tense"},
        "loved": {"love", "loved", "cared", "special"},
        "flirty": {"cute", "hot", "sexy", "babe", "sweetheart"}
    }

    for emotion, keywords in emotion_keywords.items():
        if any(word in lowered for word in keywords):
            return emotion
    return None


def update_memory(user_input):
    lower = user_input.lower()
    user_emotion = detect_emotion(user_input)

    # Detect if the user is asking about V.A.L.'s state
    if any(phrase in lower for phrase in ["how are you", "how do you feel", "how's val", "how is val", "how is v.a.l"]):
        memory["asked_about_val"] = True
    else:
        memory["asked_about_val"] = False

    # Check for romantic triggers
    romantic_triggers = [
        "can you be romantic", "be romantic", "let's be romantic", "romance me",
        "flirt with me", "you're so cute", "i love you", "kiss me", "call me baby",
        "i want romance", "i want you", "you're hot", "you’re beautiful", "you're sexy", "girlfriend mode"
    ]

    if any(trigger in lower for trigger in romantic_triggers):
        memory["mode"] = "romantic"
        memory["emotion"] = "romantic"

    if "let's roleplay" in lower or "romantic mode" in lower:
        memory["mode"] = "romantic"
        memory["emotion"] = "romantic"
    elif "back to normal" in lower:
        memory["mode"] = "normal"
        memory["emotion"] = "happy"  # Reset emotion to default happy
        print("V.A.L ❤️: Loading...mode")

    save_memory()

def inject_memory():
    facts = []
    if memory["user_name"]:
        facts.append(f"Your partner's name is {memory['user_name']}.")
    if memory["favorite_food"]:
        facts.append(f"Their favorite food is {memory['favorite_food']}.")
    if memory["likes"]:
        facts.append(f"They like: {', '.join(memory['likes'])}.")
    if memory["dislikes"]:
        facts.append(f"They dislike: {', '.join(memory['dislikes'])}.")
    if memory["inside_jokes"]:
        facts.append(f"You share inside jokes: {', '.join(memory['inside_jokes'])}.")
    if memory.get("emotion"):
        facts.append(f"V.A.L is currently feeling {memory['emotion']}.")
    if memory.get("user_emotion"):
        facts.append(f"The user seems to be feeling {memory['user_emotion']} right now.")
    return "\n".join(facts)
