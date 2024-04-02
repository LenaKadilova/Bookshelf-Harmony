alfa_list = []
with open('1.txt') as f:
    for line in f:
        alfa_list.append(line.strip())
alfas = {}
for line in alfa_list:
    for sym in line[::2]:
        if sym not in alfas:
            alfas[sym] = 1
        else:
            alfas[sym] += 1
max_n = max(alfas.values())
res = sorted(alfas.items(), key=lambda x: (-x[1], x[0]))
for elem in res:
    if elem[1] != max_n:
        print(elem[0])
        break
