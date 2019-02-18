import re
import sys
import string

###############Indexing Part Starts###############

print("-----Loading stopwords-----")
# load stop words into a list
StopWordList = []
with open('stopwords.txt', 'r') as f:
    for line in f:
        StopWordList.append(line.strip())
print(StopWordList)

print("-----Start Indexing-----")
w2s = {}  # dictonary storing the index
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
        for p in string.punctuation:
            row = row.replace(p, "")

        # indexing the content
        for word in row.lower().split():
            # not in stopwords
            if word not in StopWordList:
                # add row number into the list, then add the list in to dictionary
                w2s.setdefault(word, {}).setdefault(title, []).append(i + 1)


###############Indexing Part Ends###############

###############Searching Part Starts##############
def query_parser(query):
    '''
    This function parses the query to check its type
    and goes to a certain parser
    Input: 1) query coming from input
    Ouput: Results from different queryparsers
    '''
    wordslist = query.strip().split(" ")
    if len(wordslist) == 1:
        single_word_query(query)
    else:
        if "or" in wordslist:
            or_query(query)
        elif "and" in wordslist:
            and_query(query)
        elif "morethan" in wordslist:
            more_than_query(query)
        elif "near" in wordslist:
            near_query(query)
        else:
            and_query(query)


def single_word_query(query):
    '''
    This function deals with the single word query
    Input: 1) query coming from input (one word)
    Ouput: Retrieved results
    '''
    result = w2s.get(query, "0")
    if result != "0":
        for k, v in result.items():
            print("\t{}".format(k))
            for line in v:
                print("\t\t{} {}".format(line, highlighter(query, Content[line - 1])))
    else:
        print("\t{}".format("--"))


def or_query(query):
    '''
    This function deals with the "or" query
    Input: 1) query coming from input
    Ouput: Retrieved results
    '''

    # a list of all the query words
    wordslist = [word.strip() for word in query.split("or")]

    # list of all the titles
    titlelist = []
    for word in wordslist:
        result = w2s.get(word, "0")
        if result != "0":
            for k in result.keys():
                titlelist.append(k)
        else:
            continue

    print_result(titlelist, wordslist)


def and_query(query):
    '''
    This function deals with the "and" query
    Input: 1) query coming from input
    Ouput: Retrieved results
    '''

    # a list of all the query words
    wordslist = [word.strip() for word in query.split(" ")]
    if "and" in wordslist:
        wordslist = [word.strip() for word in query.split("and")]

    # list of all the titles
    titlelist = []
    for i in range(0, len(wordslist)):
        # if one word does not exist in the indexes, break
        if wordslist[i] not in w2s:
            titlelist = []
            break
        # all the query words exist in the indexes, find the intersection
        else:
            # for the first result, add to the title list
            if (i == 0):
                titlelist = list(w2s[wordslist[i]].keys())
            # then find the intersection of two results
            else:
                titlelist = list(set(titlelist) & set(list(w2s[wordslist[i]].keys())))

    print_result(titlelist, wordslist)


def more_than_query(query):
    '''
    This function deals with the "morethan" query
    Input: 1) query coming from input
    Ouput: Retrieved results
    '''

    wordslist = [word.strip() for word in query.split(" ")]
    match = re.search(r'[0-9]+', query)

    # 1) more than a number
    if match:
        word = wordslist[0]
        number = wordslist[2]
        if word not in w2s:
            print("\t{}".format("--"))
        else:
            titlelist = []
            # if the length of lines is morethan the number, add the story title into the list
            for k, v in w2s[word].items():
                if len(v) > int(number):
                    titlelist.append(k)
            print_result(titlelist, [word])

    # 2) one word more than another, with 4 possible cases
    else:
        leftword = wordslist[0]
        rightword = wordslist[2]
        # [1] both words do not exist
        if (leftword not in w2s) and (rightword not in w2s):
            print("\t{}".format("--"))
        # [2] the rightword exist but the left word does not exist
        elif(leftword not in w2s) and (rightword in w2s):
            print("\t{}".format("--"))
        # [3] the rightword does not exist but the left word exists, then all the stories meet the requirements
        elif(leftword in w2s) and (rightword not in w2s):
            print_result(list(w2s[leftword].keys()), [leftword, rightword])
        # [4] both exists
        else:
            titlelist = []
            for title in list(w2s[leftword].keys()):
                if title not in list(w2s[rightword].keys()):
                    titlelist.append(title)
                else:
                    if len(w2s[leftword][title]) > len(w2s[rightword][title]):
                        titlelist.append(title)
                    else:
                        continue
            print_result(titlelist, [leftword, rightword])


def near_query(query):
    '''
    This function deals with the "near" query
    Input: 1) query coming from input
    Ouput: Retrieved results
    '''

    wordslist = [word.strip() for word in query.split(" ")]
    leftword = wordslist[0]
    rightword = wordslist[2]
    titlelist = []

    # both word should be in the index
    if (leftword in w2s) and (rightword in w2s):
        titlelist = list(set(w2s[leftword].keys()) & set(w2s[rightword].keys()))
        # the length of results is not 0
        if(len(titlelist) != 0):
            # iterate through each story
            for title in titlelist:
                leftword_lines = w2s[leftword][title]
                rightword_lines = w2s[rightword][title]
                for leftword_line in leftword_lines:
                    for rightword_line in rightword_lines:
                        # compare the line number
                        if abs(leftword_line - rightword_line) <= 1:
                            print("\t{}".format(title))
                            print("\t\t{}".format(leftword))
                            print("\t\t\t{} {}".format(leftword_line, highlighter(leftword, Content[leftword_line - 1])))
                            print("\t\t{}".format(rightword))
                            print("\t\t\t{} {}".format(rightword_line, highlighter(rightword, Content[rightword_line - 1])))
    # words do not exist in the list, or titlelist length is 0
    else:
        print("\t{}".format("--"))


def highlighter(word, line):
    '''
    This function highlight the word in results
    Input: 1) The word needs to be highlighted; 2) the old line
    Output: New line
    '''
    newword = "**{}**".format(word.upper())
    newline = line.replace(word, newword)
    return newline


def print_result(titlelist, wordslist):
    '''
    This function print the retrieved results
    Input: 1) titlelist, a list which contains all the titles of stories; 2) wordlist, a list which contains all the query words
    Output: Formatted retrieved results
    '''

    # no retrieved result
    if(len(titlelist) == 0):
        print("\t{}".format("--"))
    # some retrieved results
    else:
        # iterate through the result of titles
        for title in set(titlelist):
            print("\t{}".format(title))
            # for each story, iterate through each word
            for word in wordslist:
                # the word is not in indexes (This is only for "OR" query)
                if word not in w2s:
                    print("\t\t{}".format(word))
                    print("\t\t\t{}".format("--"))
                # the word is in indexes
                else:
                    # the word exists in this story
                    if title in w2s[word].keys():
                        print("\t\t{}".format(word))
                        lines = w2s[word][title]
                        for line in lines:
                            print("\t\t\t{} {}".format(line, highlighter(word, Content[line - 1])))
                    # the word does not exist in this story
                    else:
                        print("\t\t{}".format(word))
                        print("\t\t\t{}".format("--"))


def main():
    print("Welcome to the Grimms' Fairy Tales search system!")
    while(True):
        query = input("Please enter your query: ")
        if(query != "qquit"):
            print("query = {}".format(query))
            query_parser(query)
        else:
            sys.exit()


if __name__ == '__main__':
    main()

###############Searching Part Ends###############
