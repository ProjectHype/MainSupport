import re
import os

# --- Utility Functions ---

def load_file(path):
    if not os.path.exists(path):
        print(f"[Warning] File not found: {path}")
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def parse_imports(hype_code):
    imports = re.findall(r"@import:\s*([\w\d_]+);", hype_code)
    import_urls = re.findall(r"@importurl:\s*(.*)", hype_code)
    return imports, import_urls

# --- Parse HYL (style) ---
def parse_hyl(hyl_code):
    css_output = ""
    # Simple block like: main [ property: "value" ]
    blocks = re.findall(r'([\w\-\:\"\s]+)\[([^\]]+)\]', hyl_code)
    for selector, body in blocks:
        selector = selector.strip().replace("main", "body")
        css_output += f"{selector} {{\n"
        props = re.findall(r'([\w\-]+):\s*\"([^\"]+)\"', body)
        for prop, val in props:
            css_output += f"  {prop}: {val};\n"
        css_output += "}\n\n"
    return css_output

# --- Parse HYS (script) ---
def parse_hys(hys_code):
    js_output = ""
    funcs = re.findall(r'\{function:\s*\"([\w\d_]+)\"\}:\s*\[([^\]]+)\]', hys_code)
    for name, body in funcs:
        js_output += f"function {name}() {{\n"
        sets = re.findall(r'\{set text with gather:\s*\"([\w\d_]+)\"\s*to:\s*\"([^\"]+)\"\}', body)
        for target, value in sets:
            js_output += f'  document.querySelector(`[data-gather=\"{target}\"]`).innerText = "{value}";\n'
        js_output += "}\n\n"
    return js_output

# --- Parse Hype Main File ---
def parse_hype_main(hype_code, styles, scripts, import_urls):
    # Header info
    title = re.search(r'\{windowtitle\s*-\s*\"([^\"]+)\"\}', hype_code)
    desc = re.search(r'\{hypedesc\s*-\s*\"([^\"]+)\"\}', hype_code)
    logo = re.search(r'\{windowlogo\s*-\s*\"([^\"]+)\"\}', hype_code)

    title = title.group(1) if title else "Untitled Hype App"
    desc = desc.group(1) if desc else ""
    logo = logo.group(1) if logo else ""

    html = "<!DOCTYPE html>\n<html>\n<head>\n<meta charset='utf-8'>\n"
    html += f"<title>{title}</title>\n"
    html += f"<meta name='description' content='{desc}'>\n"
    if logo:
        html += f"<link rel='icon' href='{logo}'>\n"
    for url in import_urls:
        html += f"<link href='{url.strip()}' rel='stylesheet'>\n"
    html += "<style>\n" + styles + "</style>\n"
    html += "</head>\n<body>\n"

    # Parse content blocks
    content = re.findall(r'\{header1\s*-\s*\"([^\"]+)\"\s*group:\s*\"([^\"]+)\"\s*gather:\s*\"([^\"]+)\"\}', hype_code)
    for text, group, gather in content:
        html += f"<h1 class='{group}' data-gather='{gather}'>{text}</h1>\n"

    html += "<script>\n" + scripts + "</script>\n"
    html += "</body>\n</html>"
    return html

# --- Main Runner ---
def compile_hype(main_file):
    print(f"[Hype] Compiling {main_file}...")

    main_code = load_file(main_file)
    imports, import_urls = parse_imports(main_code)

    # Load external files
    all_styles, all_scripts = "", ""

    for imp in imports:
        if os.path.exists(f"{imp}.hyl"):
            all_styles += parse_hyl(load_file(f"{imp}.hyl"))
        elif os.path.exists(f"{imp}.hys"):
            all_scripts += parse_hys(load_file(f"{imp}.hys"))
        elif os.path.exists(f"{imp}.hype"):
            all_scripts += load_file(f"{imp}.hype")
        else:
            print(f"[Warning] Unknown import: {imp}")

    html = parse_hype_main(main_code, all_styles, all_scripts, import_urls)

    output_file = main_file.replace(".hype", ".html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[Hype] ✅ Compiled successfully -> {output_file}")


if __name__ == "__main__":
    compile_hype("main.hype")
