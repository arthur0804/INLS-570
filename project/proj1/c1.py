import re
from string import punctuation

print("-----Loading stopwords-----")
# load stop words into a list
StopWordList = []
with open('stopwords.txt', 'r') as f:
    for line in f:
        StopWordList.append(line.strip())
print(StopWordList)

print("-----Start Indexing-----")
Indexes = {}  # dictonary storing the index
TitleNo = 1  # used for print the number of titles

# read the file
with open('grimms.txt', 'r') as f:
    Content = f.readlines()

for i in range(124, 9182):
    # remove all the newline and space characters
    row = Content[i].strip()

    # two cases: title and content
    # 1) the title
    if row.isupper():
        match = re.search(r'[0-9]+', row)
        # skip subtitles
        if not match:
            title = row
            print("{}\t{}" .format(TitleNo, title))
            TitleNo += 1
    # 2) the Content
    else:
        # remove all the punctuations in line
        for p in punctuation:
            row = row.replace(p, "")
        # indexing the content
        for word in row.lower().split():
            # not in stopwords
            if word not in StopWordList:
                # add row number into the list, then add the list in to dictionary
                Indexes.setdefault(word, {}).setdefault(title, []).append(i + 1)

print("-----Test Case-----")
print(Indexes['raven'])
