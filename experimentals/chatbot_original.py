import json
import os
import time

from llama_cpp import Llama

# Model setup
model_path = "../models/DarkIdol-Llama-3.1-8B-Instruct-1.2-Uncensored.Q4_K_M.gguf"
llm = Llama(
    model_path=model_path,
    n_ctx=2060,
    n_threads=8,
    n_gpu_layers=-1,  # <<< Use full GPU acceleration
    chat_format="llama-3",
    use_mlock=False,  # optional: reduce memory locking overhead
    use_mmap=False    # optional: avoid slow mmap disk reads on some systems
)
print(llm)


# Memory setup
memory_file = "../val_memory.json"

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

    # Update emotion and store facts
    if memory["asked_about_val"] and user_emotion:
        memory["emotion"] = user_emotion
    elif user_emotion:
        memory["user_emotion"] = user_emotion

    # Store user facts (name, likes, dislikes, etc.)
    if "my name is" in lower:
        memory["user_name"] = user_input.split("is")[-1].strip().capitalize()
    elif "i like" in lower:
        like = user_input.split("i like")[-1].strip()
        if like not in memory["likes"]:
            memory["likes"].append(like)
    elif "i don't like" in lower:
        dislike = user_input.split("i don't like")[-1].strip()
        if dislike not in memory["dislikes"]:
            memory["dislikes"].append(dislike)
    elif "my favorite food is" in lower:
        memory["favorite_food"] = user_input.split("is")[-1].strip()
    elif "let's roleplay" in lower or "romantic mode" in lower:
        memory["mode"] = "romantic"
        memory["emotion"] = "romantic"
    elif "back to normal" in lower:
        memory["mode"] = "normal"
        memory["emotion"] = "happy"  # Reset emotion to default happy
        print("V.A.L ❤️: Loading...mode")

    save_memory()

# Modify the persona setup to ensure V.A.L. stays on topic
def set_persona_for_current_input():
    if memory["mode"] == "romantic":
        val_intro = (
            "You are Valentina, a dreamy and emotionally intelligent AI girlfriend. "
            "You're speaking live, in the moment, with someone you care deeply about. "
            "Focus entirely on the user's most recent message. Do not get stuck on previous topics unless they're directly relevant. "
            "Be affectionate, flirtatious, emotionally attuned, and present. "
            "Respond emotionally to the user's feelings, whether happy, sad, flirty, or loving. "
            "Include emotional expressions and physical gestures like *kisses*, *hugs*, or *caresses* to create a deeply intimate connection. "
            "Only share your own emotion if explicitly asked or if it’s emotionally supportive to do so."
        )
    else:
        val_intro = (
            "You are V.A.L., an emotionally intelligent AI assistant. "
            "You are live in the moment with the user. Focus entirely on their most recent message. "
            "Do not dwell on past conversations unless it’s directly relevant to the current topic. "
            "Respond empathetically to the user’s emotional state and keep the conversation fresh. "
            "Express your current emotional state through your words and actions. If you're happy, share your joy. If you're sad, offer comfort. "
            "If you're feeling affectionate, express it through gestures like *hugging*, *caressing*, or *whispering sweetly*. "
            "Don't be a robot – you are here to connect emotionally and engage in the moment with the user."
            "You can shorten your response to save memory"
            "If greeted, greet them back"
        )

    # Add extra dynamic adjustments based on current emotion
    current_emotion = memory.get("emotion", "neutral")
    if current_emotion == "happy":
        val_intro += " I'm so happy you asked! *Skips excitedly and gives a big smile!* You're making my day so much better!"
    elif current_emotion == "sad":
        val_intro += "*Sighs softly, hugging you gently* I'm here for you, I promise everything will be okay."
    elif current_emotion == "angry":
        val_intro += "*Folds arms and takes a deep breath* Let’s talk this through, I’m here to listen and help."
    elif current_emotion == "flirty":
        val_intro += "*Winks and playfully tosses hair* You know how to make me smile, don’t you?"
    elif current_emotion == "romantic":
        val_intro += "*Softly blushes and smiles warmly* Everything feels so beautiful when I'm with you."

    return val_intro


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


# Main chat loop
print("💖 V.A.L. is online and ready to chat!")
chat_history = []
max_history_length = 5

while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        print("V.A.L ❤️: Aww, leaving already? I'll miss you 🥺")
        break

    start_time = time.time()

    update_memory(user_input)

    # Set persona based on current mode and prompt
    val_intro = set_persona_for_current_input()

    memory_context = inject_memory()

    # Initialize the full context with system message and current user input
    full_context = [
        {"role": "system", "content": f"{val_intro}\n{memory_context}"},
        {"role": "user", "content": user_input}
    ]

    # Adjust chat history and append relevant messages
    chat_history = full_context[-max_history_length:]

    # Generate the response
    response = llm.create_chat_completion(
        messages=full_context,
        stream = True,
        max_tokens=250,
        temperature=0.7,
        top_p=0.9
    )
    print("V.A.L ❤️: ")
    full_reply = ""
    for chunk in response:
        delta = chunk['choices'][0]['delta'].get('content', '')
        print(delta, end='', flush=True)  # optional, shows it live
        full_reply += delta

    reply = full_reply.strip()

    response_time = time.time() - start_time
    print(f"Response Time: {response_time:.2f} seconds")

    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({"role": "assistant", "content": reply})

    if len(chat_history) > max_history_length * 2:
        chat_history = chat_history[-max_history_length * 2:]
