with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_directory_section = False
for i, line in enumerate(lines):
    if line.strip() == 'st.stop()' and (450 < i < 570):
        continue  # Remove st.stop()
    
    # Identify the start of the College Directory section
    if 'current_quota = st.session_state.get("quota_select"' in line and not in_directory_section:
        in_directory_section = True
        new_lines.append('elif app_mode == "College Directory":\n')
        
    # Stop indenting when we reach the Javascript styling injection
    if 'JAVASCRIPT STYLING INJECTION' in line:
        in_directory_section = False

    if in_directory_section:
        if line.strip() == "":
            new_lines.append(line)
        else:
            new_lines.append('    ' + line)
    else:
        new_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
