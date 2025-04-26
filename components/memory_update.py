import json

from components.memory import memory, save_memory, update_memory, inject_memory, detect_emotion
from components.model_setup import llm


def user_input_contains_memory_trigger(user_input):
    triggers = [
        "i like", "i love", "i enjoy",
        "i hate", "i dislike", "i can't stand",
        "my favorite food", "my name is"
    ]
    user_input = user_input.lower()
    return any(trigger in user_input for trigger in triggers)

def update_memory_from_response(user_input, full_reply):
    memory_update_prompt = f"""
    Conversation:
    User: {user_input}
    V.A.L.: {full_reply}

    From this conversation, what new knowledge should be added to memory?
    ONLY reply with JSON like this:
    {{'likes': [], 'dislikes': [], 'favorite_food': '', 'user_name': ''}}.

    IMPORTANT RULES:
    - Only update if user is very clear (e.g., "I love X", "I hate Y", "My favorite food is Z", "My name is ___")
    - If unsure, reply with {{}} (do NOT guess).
    - Ignore things like 'romantic mode', 'roleplay', 'turn on light', etc.
    """

    memory_update_response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": "You are V.A.L., an AI girlfriend who updates her memory based on conversations."},
            {"role": "user", "content": memory_update_prompt}
        ],
        max_tokens=150,
        temperature=0.3,
        top_p=0.9
    )

    try:
        memory_update_content = memory_update_response['choices'][0]['message']['content']
        memory_update_json = json.loads(memory_update_content.replace("'", '"'))

        # Handle forbidden keywords
        forbidden_keywords = {"romantic mode", "normal mode", "girlfriend mode", "roleplay", "back to normal",
                              "light on", "light off"}

        # Clean likes
        if "likes" in memory_update_json:
            cleaned_likes = []
            for like in memory_update_json["likes"]:
                if like.lower() not in forbidden_keywords:
                    cleaned_likes.append(like)
                else:
                    print(f"[Ignored forbidden like: {like}]")
            memory_update_json["likes"] = cleaned_likes

        # Clean dislikes
        if "dislikes" in memory_update_json:
            cleaned_dislikes = []
            for dislike in memory_update_json["dislikes"]:
                if dislike.lower() not in forbidden_keywords:
                    cleaned_dislikes.append(dislike)
                else:
                    print(f"[Ignored forbidden dislike: {dislike}]")
            memory_update_json["dislikes"] = cleaned_dislikes

        # Update memory safely
        for like in memory_update_json.get("likes", []):
            if like not in memory["likes"]:
                memory["likes"].append(like)

        for dislike in memory_update_json.get("dislikes", []):
            if dislike not in memory["dislikes"]:
                memory["dislikes"].append(dislike)

        if memory_update_json.get("favorite_food"):
            memory["favorite_food"] = memory_update_json["favorite_food"]

        if memory_update_json.get("user_name"):
            memory["user_name"] = memory_update_json["user_name"]

        # Fix contradictions
        memory["likes"] = [item for item in memory["likes"] if item not in memory["dislikes"]]
        memory["dislikes"] = [item for item in memory["dislikes"] if item not in memory["likes"]]

        save_memory()
        print("\n[Memory updated successfully!]")

    except Exception as e:
        print("\n[Failed to update memory]", e)
