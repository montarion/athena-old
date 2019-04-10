import csv, sys
oldvidlist = []
with open('realvidlinks.csv', 'r') as f:
    reader = csv.reader(f, delimiter=',')
    for row in reader:
        oldvidlink = row[0]
        oldvidlist.append(oldvidlink)

with open('realvidlinks.csv', 'a') as f:
    writer = csv.writer(f)
    line = sys.argv[1]
    if line not in oldvidlist:
        print('added!')
        writer.writerow([line])
        print("only {} left to go!".format(str(365-len(oldvidlist))))
    else:
        print("that's a duplicate!")
        print("only {} left to go!".format(str(365-len(oldvidlist))))


