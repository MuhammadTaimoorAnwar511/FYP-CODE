import subprocess

if __name__ == "__main__":

    print("#"*60)
    print(f"Fetching Price Data")
    subprocess.run(["python", "price.py"])

    print("#"*60)
    print(f"Doing some Formating")
    subprocess.run(["python", "Formating.py"])

    print("#"*60)
    print(f"Fetching Open Interest Data")
    subprocess.run(["python", "OpenInterest.py"])

    print("#"*60)
    print(f"Doing some Formating")
    subprocess.run(["python", "Formating.py"])

    print("#"*60)
    print(f"Fetching Long Short Ratio")
    subprocess.run(["python", "LongShort.py"])
    
    print("#"*60)
    print(f"Fetching Fear and Greed Index")
    subprocess.run(["python", "FearGreed.py"])

    print("#"*60)
    print(f"Doing some Formating")
    subprocess.run(["python", "Formating.py"])

    print("#"*60)
    print(f"Running Dummy File")
    subprocess.run(["python", "Dummy.py"])

    print("#"*60)
    print(f"Fetching Twitter Index")
    subprocess.run(["python", "Twitter.py"])

    print("#"*60)
    print(f"Doing some Formating")
    subprocess.run(["python", "Formating.py"])

    print("#"*60)
    print(f"Checking Data Range")
    subprocess.run(["python", "Month.py"])

    print("#"*60)
    print(f"Pushing Data to Google Drive")
    subprocess.run(["python", "Push.py"])


    print("#"*60)
