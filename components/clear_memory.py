from components.memory import memory, save_memory

def clear_memory_sequence():
    print("\nV.A.L ❤️: Are you sure you want me to forget everything about you? 🥺 (yes/no)")
    confirm = input("You: ").strip().lower()

    if confirm in ["yes", "y"]:
        memory["likes"] = []
        memory["dislikes"] = []
        memory["inside_jokes"] = []
        memory["favorite_food"] = ""
        memory["user_name"] = ""
        memory["mode"] = "normal"
        memory["emotion"] = "neutral"
        memory["user_emotion"] = "neutral"
        save_memory()
        print("\n[Memory has been cleared! 🧹💖]")
        return True
    else:
        print("\nV.A.L ❤️: Yay!! I'm so happy you decided to keep our memories 🥰")
        return False
