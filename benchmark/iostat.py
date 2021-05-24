import sys, subprocess, re
from time import time, sleep

HEADERS = ["timestamp","tps","kB_read/s","kB_wrtn/s","kB_dscd/s","kB_read","kB_wrtn","kB_dscd"]

if __name__ == "__main__":
    entries = [HEADERS]

    if len(sys.argv) != 4:
        print("Invalid parameters! Usage: python3 iostat.py <OUTPUT_FILENAME> <MINUTES> <STORAGE_DEVICE>")
        sys.exit(-1)

    output_file = sys.argv[1]
    duration_in_minutes = int(sys.argv[2])
    storage_device = sys.argv[3]

    # Print headers to know which values correspond to what metrics
    print(HEADERS)
    
    # Surround with try/except to save progress
    try:
        for _ in range(duration_in_minutes*60):
            # Execute iostat
            iostat_exec = subprocess.run(["iostat", "-d", f"{storage_device}"], capture_output=True)
            output = iostat_exec.stdout.decode("utf-8")
            
            # Parse values and add timestamp
            values = re.findall(f"(?<={storage_device})(.*?)(?=\n)", output)[0].split()
            entry = [str(int(time()))] + values

            # Print output to view results
            print(entry)

            # Save values and sleep
            entries.append(entry)
            sleep(1)

        # Tranform to CSV lines
        entries = map(lambda x: ",".join(x)+"\n", entries)

        # Save to file
        with open(output_file, "w") as f:
            f.writelines(entries)

    # If exception occurs, save data
    except:
        # Print error
        print(sys.exc_info()[0])

        # Tranform to CSV lines
        entries = map(lambda x: ",".join(x)+"\n", entries)

        # Save to file
        with open(output_file, "w") as f:
            f.writelines(entries)