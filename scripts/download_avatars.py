import urllib.request
import os
import time

def download_avatars():
    out_dir = os.path.join("frontend", "public", "avatars")
    os.makedirs(out_dir, exist_ok=True)
    
    # We need 500 unique faces
    for i in range(1, 501):
        filename = os.path.join(out_dir, f"{i}.jpg")
        if not os.path.exists(filename):
            print(f"Downloading {i}.jpg...")
            try:
                req = urllib.request.Request(
                    'https://thispersondoesnotexist.com/', 
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                with urllib.request.urlopen(req) as response:
                    with open(filename, 'wb') as f:
                        f.write(response.read())
                time.sleep(1) # Be polite
            except Exception as e:
                print(f"Failed to download {i}: {e}")

if __name__ == "__main__":
    download_avatars()
