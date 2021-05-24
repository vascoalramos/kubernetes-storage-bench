import sys, subprocess, re
from time import time

HEADERS = ["timestamp","CPU_usr","CPU_sys","CPU_idl","CPU_wai","CPU_stl","MEM_used","MEM_free","MEM_buff", "MEM_cach", "NET_recv", "NET_send"]

if __name__ == "__main__":
    entries = [HEADERS]

    if len(sys.argv) != 3:
        print("Invalid parameters! Usage: python3 dstat.py <OUTPUT_FILENAME> <MINUTES>")
        sys.exit(-1)

    output_file = sys.argv[1]
    duration_in_minutes = int(sys.argv[2])

    # Print headers to know which values correspond to what metrics
    print(HEADERS)

    # Surround with try/except to save progress
    try:
        # Execute dstat
        dstat = subprocess.Popen("dstat --cpu --mem --net --noheaders", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Ignore headers
        for _ in range(2):
            dstat.stdout.readline()

        # Read from dstat (it prints every second)
        for _ in range(duration_in_minutes*60):
            # Wait for output from dstat
            output = dstat.stdout.readline().decode("utf-8")
            timestamp = int(time())
            
            # Get metrics to process
            cpu, mem, net = output.split("|")

            # Add entry to entries
            entry = [str(timestamp)] + cpu.split() + mem.split() + net.split()
            entries.append(entry)

            # Print output to view results
            print(entry)

        # End dstat process
        dstat.terminate()
        
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