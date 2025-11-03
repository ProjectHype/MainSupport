import re

def run_hype(code):
    sections = {}
    current_section = None
    
    # Split into lines and handle each
    for line in code.splitlines():
        line = line.strip()
        if not line:
            continue
        
        # Detect new section, like {hypewindow}:
        if line.startswith("{") and line.endswith("}:"):
            current_section = line.strip("{}: ")
            sections[current_section] = []
            continue
        
        # Add commands to the current section
        if current_section:
            sections[current_section].append(line)
    
    # Interpret hypewindow (metadata)
    window = {}
    for line in sections.get("hypewindow", []):
        match = re.match(r'\[hype\s*-\s*(\w+):\s*\("(.+)"\)\]!', line)
        if match:
            key, value = match.groups()
            window[key] = value
    
    # Interpret hypebody (execution)
    for line in sections.get("hypebody", []):
        match = re.match(r'\[hype\s*-\s*(\w+):\s*\("(.+)"\)\]!', line)
        if match:
            key, value = match.groups()
            if key == "print":
                print(value)
    
    print(f"\n🏷️ Window Info: {window}")

# Example Hype code
code = """
{hypewindow}:
    [hype - windowtitle: ("I'm coding in Hype!")]!
    [hype - author: ("@you")]!

{hypebody}:
    [hype - print: ("Hello world from Hype!")]!
"""

run_hype(code)
