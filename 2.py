import csv
import json

list_line = []
with open('2.csv') as f:
    csv_file = csv.reader(f, delimiter=';')
    for line in csv_file:
        list_line.append(line)
lines = {}
for elem in list_line:
    if elem[0] not in lines:
        lines[elem[0]] = [elem[1]]
    else:
        lines[elem[0]].append(elem[1])
with open('result.json', 'w') as f:
    json.dump(lines, f, indent=4)

print(lines)
