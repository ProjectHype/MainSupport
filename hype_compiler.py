import os
import re

# === Hype Compiler ===
# Converts .hype files into HTML + JS apps

def compile_hype_to_html(input_path, output_dir="dist"):
    # Read the Hype file
    with open(input_path, "r", encoding="utf-8") as f:
        hype_code = f.read()

    # Create output folder
    os.makedirs(output_dir, exist_ok=True)

    # === Extract app title ===
    title_match = re.search(r'title\s+"([^"]+)"', hype_code)
    app_title = title_match.group(1) if title_match else "Hype App"

    # === Extract page content ===
    page_match = re.search(r'page\s+(\w+)\s*{([^}]*)}', hype_code, re.DOTALL)
    page_name = page_match.group(1) if page_match else "main"
    page_content = page_match.group(2).strip() if page_match else ""

    # === Extract script block ===
    script_match = re.search(r'script\s*{([^}]*)}', hype_code, re.DOTALL)
    script_content = script_match.group(1).strip() if script_match else ""

    # === Convert Hype components to HTML ===
    html_lines = []
    for line in page_content.splitlines():
        line = line.strip()

        # Text
        if line.startswith("text"):
            text_value = re.findall(r'"([^"]+)"', line)
            if text_value:
                html_lines.append(f"<h1>{text_value[0]}</h1>")

        # Button
        elif line.startswith("button"):
            parts = re.findall(r'"([^"]+)"|onClick\s+(\w+)', line)
            button_label = parts[0][0] if parts and parts[0][0] else "Button"
            onclick_func = parts[1][1] if len(parts) > 1 and parts[1][1] else None
            onclick_attr = f' onclick="{onclick_func}()"' if onclick_func else ""
            html_lines.append(f"<button{onclick_attr}>{button_label}</button>")

        # Display element
        elif line.startswith("display"):
            match = re.search(r'display\s+(\w+)', line)
            if match:
                id_name = match.group(1)
                html_lines.append(f'<p id="{id_name}Display">0</p>')

    html_body = "\n    ".join(html_lines)

    # === Convert script block to JavaScript ===
    js_lines = []

    # Variables
    for var_decl in re.findall(r'var\s+(\w+)\s*=\s*([^\n]+)', script_content):
        name, value = var_decl
        js_lines.append(f"let {name.strip()} = {value.strip()};")

    # Functions
    func_blocks = re.findall(r'func\s+(\w+)\s*\(\)\s*{([^}]*)}', script_content, re.DOTALL)
    for func_name, func_body in func_blocks:
        body_lines = []
        for cmd in func_body.strip().splitlines():
            cmd = cmd.strip()
            if cmd.startswith("update()"):
                body_lines.append("update();")
            elif "=" in cmd:
                body_lines.append(cmd)
        js_lines.append(f"function {func_name}() {{\n    " + "\n    ".join(body_lines) + "\n}}")

    # === Add update() function ===
    js_lines.append("""
function update() {
  document.getElementById("counterDisplay").textContent = "Counter: " + counter;
}
    """)

    final_js = "\n".join(js_lines)

    # === Generate index.html ===
    html_output = f"""<!DOCTYPE html>
<html>
<head>
  <title>{app_title}</title>
  <style>
    body {{
      font-family: 'Inter', sans-serif;
      background: #121212;
      color: white;
      text-align: center;
      padding: 40px;
    }}
    button {{
      background: #4f9cff;
      border: none;
      padding: 10px 20px;
      margin: 10px;
      border-radius: 8px;
      color: white;
      font-size: 16px;
      cursor: pointer;
    }}
  </style>
</head>
<body>
  <div id="app">
    {html_body}
  </div>
  <script>
  {final_js}
  </script>
</body>
</html>"""

    # Write HTML file
    html_path = os.path.join(output_dir, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_output)

    print(f"✅ Hype App compiled successfully → {html_path}")


# === Example usage ===
if __name__ == "__main__":
    compile_hype_to_html("app.hype")
