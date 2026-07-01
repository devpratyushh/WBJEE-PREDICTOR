with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Emojis to remove
replacements = {
    "🌟 Elite State Univ": "Elite State Univ",
    "🏛️ Top Govt Engg": "Top Govt Engg",
    "🏛️ State Govt Engg": "State Govt Engg",
    "🏛️ State University": "State University",
    "💊 Pharmacy College": "Pharmacy College",
    "🎓 Private University": "Private University",
    "🏢 Private College": "Private College",
    "🏢 Top Private Colleges": "Top Private Colleges",
    "🔮 Predict Colleges": "Predict Colleges",
}

for old, new in replacements.items():
    code = code.replace(old, new)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)
