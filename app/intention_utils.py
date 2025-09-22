# --- check for more results ---
more_results_phrases = [
    "more examples", "show me more", "different products",
    "another product", "other options", "more results"
]

def check_more_results(query):
    text = query.lower()
    for phrase in more_results_phrases:
        if phrase in text:
            return True
    return False

#--- check for greetings ---
greetings = ["hello", "hey", "hi", "good morning", "good evening"]
def check_greetings(query):
    text = query.lower().strip()
    for g in greetings:
        if text.startswith(g):
            # --- remove greeting part ---
            remaining = text[len(g):].strip(",. ")
            if remaining:  
                return "query", remaining  
            else:
                return "greeting", g      
    return "query", text    