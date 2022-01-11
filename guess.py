#! /usr/bin/python3

import sys, re, time

theWordListPath = 'words'
theTimeLimit = None # seconds

def readWords() -> list[str]:
    with open(theWordListPath) as file:
        return [line.strip() for line in file.readlines()]

def joinSetAndList(s: set[str], l: list[str]) -> str:
    s = set.union(set(l))
    return setToStr(s)

def setToStr(s: set[str]):
    return ''.join(list(s))

class Clues:
    clues = {}
    cacheHits = 0
    cacheMisses = 0

    @staticmethod
    def makeClues(pattern: str, inChars: str, outChars: str):
        # Try to use an existing Clues object, because
        # it caches the elimated word list
        clues = Clues(pattern, inChars, outChars)
        existingClues = Clues.clues.get(clues)
        if existingClues is not None:
            Clues.cacheHits += 1
            return existingClues
        Clues.cacheMisses += 1
        Clues.clues[clues] = clues
        # print(f"New Clues: {clues}")
        return clues

    def __init__(self, pattern: str, inChars: str, outChars: str):
        self.pattern = pattern
        self.re = re.compile(pattern)

        inSet = set(pattern)
        if '.' in pattern:
            inSet.remove('.')
        self.inChars = frozenset(inSet.union(set(inChars)))

        self.outChars = frozenset(outChars)
        self.outPattern = re.compile('|'.join(list(self.outChars))) if len(self.outChars) > 0 else None

        self._words = None
        self._count = None
    
    def __str__(self) -> str:
        return f"{self.pattern}/{setToStr(self.inChars)}/{setToStr(self.outChars)}"

    def testWord(self, word):
        if not self.re.match(word): return False
        for ch in self.inChars:
            if ch not in word: return False
        if self.outPattern is not None and self.outPattern.search(word): return False
        return True

    def getWords(self, words):
        if (self._words is None):
            self._words = [word for word in words if self.testWord(word)]
        return self._words

    def countWords(self, words):
        if (self._count is not None): return self._count
        if (self._words is not None): return len(self._words)

        result = 0
        for word in words: 
            if self.testWord(word): result += 1
        self._count = result
        return result

    def valueOfGuess(self, guess: str, wordList: list[str]):
        words = self.getWords(wordList)
        lenWords = len(words)

        eliminations = lenWords*1.0
        for word in words:
            clues = self.update(guess, word)
            eliminations -= clues.countWords(words)/lenWords
        return eliminations/lenWords

    def update(self, guess: str, actual: str):
        outChars = [c for c in guess if c not in actual]
        inChars = [c for c in guess if c in actual]

        pattern = list(self.pattern)
        for i in range(len(actual)):
            if guess[i] == actual[i]: pattern[i] = actual[i]

        return Clues.makeClues(''.join(pattern), joinSetAndList(self.inChars, inChars), joinSetAndList(self.outChars, outChars))

    def __hash__(self):
        return hash(str(self))
    
    def __eq__(self, o: object) -> bool:
        if (not self.pattern == o.pattern): return False
        if (not self.inChars == o.inChars): return False
        if (not self.outChars == o.outChars): return False
        return True
    
def main(argv=sys.argv):
    print ("Wordl Guesser")
    ### DEBUG
    # argv = [ '.....', '', '' ]
    # argv = [ '..a..', 'abr', 'zteg' ]
    words = readWords()
    clues = Clues.makeClues(argv[1], argv[2], argv[3])

    possibilities = len(clues.getWords(words))
    print(f"There are {possibilities} possibilities left")
    if possibilities <= 2:
        for word in clues.getWords(words): print(word)
        return 0

    bestGuess = ""
    bestValue = 0
    startTime = time.process_time()
    currentTime = startTime
    count = 0

    for guess in words:
        value = clues.valueOfGuess(guess, clues.getWords(words))

        count += 1
        currentTime = time.process_time()
        totalTime = currentTime - startTime
        if theTimeLimit is not None and totalTime > theTimeLimit: return 1

        if value < bestValue: continue
        if value == bestValue and guess not in clues.getWords(words): continue

        print(f"...Found {guess}:{value:.1%} ({totalTime:.1f} seconds)")
        bestGuess = guess
        bestValue = value


    print(f"If you guess '{bestGuess}' you'll eliminate {bestValue:.1%}. ({totalTime:.1f} seconds)")

    return 0

if __name__ == "__main__":
    sys.exit(main())
