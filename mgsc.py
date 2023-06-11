# python -m pip install selenium
# python -m pip install webdriver-manager
# python -m pip install beautifulsoup4
# python -m pip install Pillow

import os
from io import BytesIO
from PIL import Image
from base64 import b64decode
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


def scraper(url):
    # Set options for webdriver
    options = Options()
    options.headless = True  # hide GUI
    options.add_argument("--window-size=1920,1080")  # set window size to native GUI size
    options.add_argument("start-maximized")  # ensure window is full-screen
    options.add_argument("--log-level=3")  # suppress debug log

    # Configure Chrome browser to not load images and javascript
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})

    # Creating a new driver with ChromeDriverManager based in the service options
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(url)

    # Wait for page to load until expected conditions
    WebDriverWait(driver, timeout=5).until(
        EC.presence_of_element_located((By.ID, "XXXXXX")),
        EC.presence_of_element_located((By.CLASS_NAME, "XXXXXXXXXX"))
    )

    # Getting content
    content = driver.page_source

    # Parsing content
    soup = BeautifulSoup(content, "html.parser")

    print(" ")

    # Soup Query 1: Getting title
    header = soup.find("X", {"XXXXX": "XXXXXXXXXXX"})
    title = header.text

    # Soup Query 2: Getting pages
    slider = soup.find("XXX", {"XX": "XXXXXX"})
    pages = slider.find_all("XXX")

    # Detecting current chapter
    chap = url.split('/')[-1].split('#')[-1]

    # Detecting sources
    sources = len(pages)
    print("Detected pages: " + str(sources))

    # Making the output dir
    path = f"{os.getcwd()}\\{title}\\Cap. {chap}\\"
    os.makedirs(path)

    print("Created destination: " + path)

    print(f"\nDownloading {title} - Cap. {chap} ... \n")

    count = 1

    for page in pages:
        url = page["src"]

        # Forming the filename from last link resource
        filename = url.split('/')[-1]

        # Setting output
        out = path + "\\" + filename

        # Using the requests module gives a 1020 error code (missing headers to authentication), so as alternative:

        driver.get(url)

        # Using javascript to save a base64 img (a lite alternative to selenium-wire)
        b64img = driver.execute_script(r'''
        var img = document.getElementsByTagName("img")[0];
        var canvas = document.createElement("canvas");
        canvas.width = img.width;
        canvas.height = img.height;
        var ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0);
        var dataURL = canvas.toDataURL("image/png");
        return dataURL.replace(/^data:image\/(png|jpg);base64,/, "");
        ''')

        # Decode from base64, translate to bytes and write to PIL image
        raw = Image.open(BytesIO(b64decode(b64img)))
        img = raw.convert("RGB")
        img.save(out)

        # Progress stats
        print(filename + " was successful downloaded from:\n" + url)
        print(f"progress ({((count / sources) * 100):.1f}%): {count}/{sources} \n")
        count += 1


if __name__ == "__main__":
    import sys
    import getopt

    # Arguments
    arg_url = ""
    arg_help = "{0} -u <url>".format(sys.argv[0])

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:", ["help", "url="])
    except:
        # Any problem returns the helper arg.
        print(arg_help)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)
            sys.exit(2)
        elif opt in ("-u", "--url"):
            arg_url = arg

    # Starting program
    scraper(arg_url)
