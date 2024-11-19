import http.client
import sys
import os
import time
import threading
from urllib.parse import urlparse

def fetch_file(target_url):
    global received_bytes, downloading_active

    url_info = urlparse(target_url)
    server = url_info.hostname
    resource_path = url_info.path or '/'

    conn = (
        http.client.HTTPSConnection(server)
        if url_info.scheme == "https"
        else http.client.HTTPConnection(server)
    )
    conn.request("GET", resource_path)
    response = conn.getresponse()

    if response.status != 200:
        downloading_active = False
        print(f"Error: Could not download file, HTTP {response.status}")
        return

    file_name = os.path.basename(resource_path)
    if not file_name:
        file_name = "file_downloaded"

    with open(file_name, "wb") as output_file:
        while True:
            data_chunk = response.read(1024)
            if not data_chunk:
                break
            with thread_lock:
                received_bytes += len(data_chunk)
            output_file.write(data_chunk)

    conn.close()
    print(f"File successfully downloaded as: {file_name}")
    downloading_active = False

def display_progress():
    global received_bytes, downloading_active

    last_check = 0
    while downloading_active:
        time.sleep(1)
        with thread_lock:
            new_data = received_bytes - last_check
            last_check = received_bytes
        print(f"Downloaded: {received_bytes} bytes (+{new_data} bytes/s)")

if len(sys.argv) < 2:
    print("Usage: python script.py <URL>")
    sys.exit(1)

download_url = sys.argv[1]

received_bytes = 0
downloading_active = True
thread_lock = threading.Lock()

download_task = threading.Thread(target=fetch_file, args=(download_url,))
progress_task = threading.Thread(target=display_progress)

download_task.start()
progress_task.start()

download_task.join()
progress_task.join()
