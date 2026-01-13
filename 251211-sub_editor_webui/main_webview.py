import webview
import os
from api import Api

def main():
    # Get absolute path to the HTML file
    html_path = os.path.abspath("ui_overhaul.html")
    api = Api(None) # Window not created yet
    
    window = webview.create_window(
        'Voice Subtitle Editor', 
        url=f'file://{html_path}',
        js_api=api,
        width=1200,
        height=900,
        background_color='#0f172a'
    )
    api.window = window
    webview.start(debug=True)

if __name__ == '__main__':
    main()
