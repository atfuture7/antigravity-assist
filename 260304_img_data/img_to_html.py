import base64
import mimetypes
import os
import sys

def image_to_data_uri(image_path):
    """Converts an image file to a Base64 data URI."""
    if not os.path.exists(image_path):
        print(f"Error: File {image_path} does not exist.")
        return None
    
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = 'image/png'  # Fallback
        
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
    return f"data:{mime_type};base64,{encoded_string}"

def create_html_with_image(data_uri, output_path):
    """Creates an HTML file with the embedded image."""
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Embedded Image</title>
    <style>
        body {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            background-color: #f0f2f5;
            font-family: 'Inter', -apple-system, sans-serif;
        }}
        .container {{
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            text-align: center;
        }}
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin-top: 1rem;
        }}
        h1 {{
            color: #333;
            margin-bottom: 0.5rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Converted Image</h1>
        <p>This image is embedded as a Data URI.</p>
        <img src="{data_uri}" alt="Converted Image">
    </div>
</body>
</html>
"""
    with open(output_path, "w") as html_file:
        html_file.write(html_content)
    print(f"HTML file saved to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python img_to_html.py <image_path> [output_path]")
        sys.exit(1)
        
    input_image = sys.argv[1]
    output_html = sys.argv[2] if len(sys.argv) > 2 else "output.html"
    
    uri = image_to_data_uri(input_image)
    if uri:
        create_html_with_image(uri, output_html)
