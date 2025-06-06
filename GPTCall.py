from openai import OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open("output.json", "r", encoding="utf-8") as f:
    music_data = json.load(f)

prompt = f"""
Ich habe ein Musikstück in JSON-Form. Beschreibe mir bitte:
- um welche Art Stück es sich handelt (z.B. Etüde, Lied, etc.)
- welche Tonart,
- welches rhythmische Muster,
- ob es stilistisch zu einer bestimmten Epoche oder Komponist passt.
- und für welche Art von Spieler es sich eignet (z.B. Anfänger, Fortgeschrittener, etc.)


Hier ist das Musikstück:
{json.dumps(music_data, indent=2)}
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Du bist ein Musikexperte."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    max_tokens=500
)

print(response.choices[0].message.content)
