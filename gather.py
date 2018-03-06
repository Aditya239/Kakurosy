"""
Scrapes as many new puzzles from the internet
as desired and adds them to the local puzzle bank
"""
import urllib2
import sys
import re
import time
from bs4 import BeautifulSoup

class GatherError(Exception):
    """
    An application specific error.
    """
    pass

if len(sys.argv)!=2:
    raise GatherError("Wrong number of arguments! Enter number of puzzles to gather as argument.\n" \
          "Example Usage: python gather.py 10 to gather 10 puzzles")
try:
    numpuzzles = int(sys.argv[1])
    assert numpuzzles >= 0
except (ValueError, AssertionError):
    raise GatherError("Number of puzzles to gather must be a non-negative integer.")

puzzlebank = []
try:
    file = open("savedpuzzles.txt", "r")
except IOError:
    print "Could not acquire read access to file: savedpuzzles.txt"
    sys.exit()
with file:
    for line in file:
        if line.rstrip("\r\n").isdigit():
            puzzlebank = puzzlebank + [int(line)]
    file.close()
print 'Currently there are %d unique puzzles in the local puzzle bank!'%(len(set(puzzlebank)))
print 'Note: A second\'s pause is good practice while scraping online. Be grateful! Internet King Lear:' \
      '\n\"How sharper than a serpent\'s tooth it is to have a thankless scraper!\"'
try:
    file = open("savedpuzzles.txt", "a")
except IOError:
    print "Could not acquire write access to file: savedpuzzles.txt"
    sys.exit()
with file:
    cntup = 0
    timeout = numpuzzles
    print 'Progress:'
    while cntup < timeout:
        kakuropage = urllib2.urlopen('http://www.kakuroconquest.com/')
        time.sleep(1)
        kakurosoup = BeautifulSoup(kakuropage,'html.parser')
        puzzleid = 0
        for souptitle in kakurosoup.find_all(class_="text1"):
            content = souptitle.text
            if (content[1]=='N'):
                puzzlenumber = re.search(r'\d+$', content.strip()).group()
                puzzleid = int(puzzlenumber)
        if puzzleid in puzzlebank:
            continue
        else:
            cntup = cntup + 1
            numeq = (cntup*10)/timeout
            sys.stdout.write('\r')
            sys.stdout.write("[%-10s] %f%%" % ('=' * numeq, float(cntup*100)/timeout))
            sys.stdout.flush()
        file.write(str(puzzleid)+'\n')
        for elem in kakurosoup.find_all(class_="cellTotal"):
            for elemitem in elem.find_all('input'):
                addr = elemitem['name']
                total = int(elemitem['value'])
                file.write(str(total)+addr[5].encode('ascii')+str(int(addr[7]))+str(int(addr[9]))+'\n')
        for elem in kakurosoup.find_all(class_="cellNumber"):
            for elemitem in elem.find_all('input'):
                addr = elemitem['name']
                file.write('e'+str(int(addr[5])) + str(int(addr[7])) + '\n')
    print ('\nPuzzle bank updated with %d new Kakuro puzzles!'%(numpuzzles))
    file.close()