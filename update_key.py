
import os

target_file = ".env"
new_key = "AIzaSyB7R75KUagnezD4jAlWUFk4pk3Gouhm-Gg"

if os.path.exists(target_file):
    with open(target_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace the placeholder
    new_content = content.replace("GEMINI_API_KEY=your_gemini_api_key_here", f"GEMINI_API_KEY={new_key}")
    
    # Also replace if it was already set to something else just in case, 
    # but relying on the specific placeholder is safer if I know the state.
    # If the placeholder isn't there, we might need a regex or line replacement.
    
    lines = content.splitlines()
    with open(target_file, "w", encoding="utf-8") as f:
        for line in lines:
            if line.startswith("GEMINI_API_KEY="):
                f.write(f"GEMINI_API_KEY={new_key}\n")
            else:
                f.write(line + "\n")
                
    print(f"Updated {target_file} with new API Key.")
else:
    print(f"{target_file} not found.")
