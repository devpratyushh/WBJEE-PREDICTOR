with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_button_block = False
button_indent = 12
new_indent = 4

for i, line in enumerate(lines):
    if line.strip() == 'if st.button("🔮 Predict Colleges", use_container_width=True, type="primary"):':
        new_lines.append(line.replace('if st.button', 'predict_clicked = st.button'))
        new_lines.append(' ' * new_indent + 'if predict_clicked:\n')
        in_button_block = True
        continue
    
    # Check if we are exiting the app_mode == "Rank Predictor" block entirely
    if in_button_block and not line.startswith(' ' * (button_indent + 4)) and line.strip() != "":
        # We exited the block that was inside if st.button
        in_button_block = False

    if in_button_block:
        if line.strip() == "":
            new_lines.append(line)
        else:
            # Shift everything left by 8 spaces (from 12/16 to 4/8)
            new_lines.append(line[8:])
    else:
        new_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
