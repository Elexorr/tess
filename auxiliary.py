def find_authors(l):
    authors = []
    for i in range (0, len(l)):
        if l[i] in authors:
            pass
        else:
            authors.append(l[i])
    print(authors)


def find_exptimes(e):
    exptimes = []
    for i in range (0, len(e)):
        if str(e[i])[0:4] in exptimes:
            pass
        else:
            exptimes.append(str(e[i])[0:4])
    for k in range (0, len(exptimes)):
        if '.' in exptimes[k]:
            exptimes[k] = exptimes[k][0:3]
    print(exptimes)