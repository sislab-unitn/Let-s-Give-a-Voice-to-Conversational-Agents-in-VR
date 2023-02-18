import sys
import os

# delete results file
results_path = "results.txt"
with open(results_path, "w") as f:
    pass
for filename in os.listdir(sys.argv[1]):
    times = []
    path = os.path.join(sys.argv[1], filename)
    print(path)
    with open(path, "rb") as f:
        file = f.read()
        splitted = file.split(b'custom_time_stamp')
        for line in splitted[1:]:
            time = line[4:20].strip()
            # print(time)
            times.append(time) 
    times = [float(t.decode("utf-8")) for t in times]
    # print ("Standard deviation: ", (sum([(t - sum(times)/len(times))**2 for t in times])/len(times))**0.5)
    with open(results_path, "a") as f:
        f.write(filename + "\n")
        if times:
            f.write(f'Number of elements {str(len(times))}' + "\n")
            f.write("Average: " + str(sum(times)/len(times)) + "\n")
            f.write("Max: " + str(max(times)) + "\n")
            f.write("Min: " + str(min(times)) + "\n")
            f.write("Standard deviation: " + str((sum([(t - sum(times)/len(times))**2 for t in times])/len(times))**0.5) + "\n")
            f.write("\n")
        
    unity_times = []
    with open(path, "rb") as f:
        file = f.read()
        splitted = file.split(b'UnityTime')
        for line in splitted[1:]:
            time = line[3:6].strip()
            print(time)
            unity_times.append(time) 
    
    unity_times = [float(t.decode("utf-8"))/1000 for t in unity_times]
    if unity_times:
        with open(results_path, "a") as f:
            f.write('Unity Times' + "\n")
            f.write(f'Number of elements {str(len(unity_times))}' + "\n")
            f.write("Average: " + str(sum(unity_times)/len(unity_times)) + "\n")
            f.write("Max: " + str(max(unity_times)) + "\n")
            f.write("Min: " + str(min(unity_times)) + "\n")
            f.write("Standard deviation: " + str((sum([(t - sum(unity_times)/len(unity_times))**2 for t in unity_times])/len(unity_times))**0.5) + "\n")
            
            f.write("\n")
        