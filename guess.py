#! /usr/bin/python3

import sys, time

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

def inCharsToSets(s: str):
    return [set(ins) for ins in s.split('/')]

class CorrectClue:
    # word has to match pattern of letters with known locations

    def __init__(self, chars: list[str]):
        self.chars = chars

    def match(self, word: str) -> bool:
        for (w, s) in zip(word, self.chars):
            if s != '.' and w != s: return False
        return True

    def combine(self, clue):
        return CorrectClue([s if s != '.' else c for (s,c) in zip(self.chars, clue.chars)])

    def __str__(self) -> str:
        return ''.join(self.chars)

    @staticmethod
    def parse(s: str):
        return CorrectClue(list(s))

    @staticmethod
    def fromGuess(guess: str, word: str):
        return CorrectClue([(g if g == w else '.') for (w,g) in zip(word, guess)])

class NotFoundClue:
    def __init__(self, chars: list[str]):
        self.chars = chars

    def match(self, word: str) -> bool:
        for c in self.chars:
            if c in word: return False
        return True

    def combine(self, clue):
        return NotFoundClue(self.chars + clue.chars)

    def __str__(self) -> str:
        return ''.join(self.chars)

    @staticmethod
    def parse(s: str):
        return NotFoundClue(list(s))

    @staticmethod
    def fromGuess(guess: str, word: str):
        return NotFoundClue([g for g in guess if g not in word])


class ElsewhereClue:
    # If char is *elsewhere* in word, it shouldn't be in this position

    def __init__(self, chars: list[set[str]]):
        self.chars = chars

    def match(self, word: str) -> bool:
        for (ins, wordChar) in zip(self.chars, word):
            if wordChar in ins: return False
            # But it must be in the word somewhere
            for inChar in ins: 
                if inChar not in word: return False
        return True

    def combine(self, clue):
        return ElsewhereClue([s.union(c) for (s,c) in zip(self.chars, clue.chars)])

    def __str__(self) -> str:
        return '/'.join([''.join(c) for c in self.chars])

    @staticmethod
    def parse(s: str):
        return ElsewhereClue([set(list(chars)) for chars in s.split('/')])

    @staticmethod
    def fromGuess(guess: str, word: str):
        return ElsewhereClue([(set(g) if g in word and g != w else set())for (g,w) in zip(guess, word)])

class Clues:
    clues = {}

    @staticmethod
    def makeClues(correct: CorrectClue, elsewhere: ElsewhereClue, notFound: NotFoundClue):
        # Try to use an existing Clues object, because
        # it caches the eliminated word list
        clues = Clues(correct, elsewhere, notFound)
        existingClues = Clues.clues.get(clues)
        if existingClues is not None:
            return existingClues
        Clues.clues[clues] = clues
        return clues

    def __init__(self, correct: CorrectClue, elsewhere: ElsewhereClue, notFound: NotFoundClue):
        self.correct = correct
        self.elsewhere = elsewhere
        self.notFound = notFound

        self._words = None
        self._count = None
    
    def __str__(self) -> str:
        return ' '.join(f"'{s}'" for s in [self.correct, self.elsewhere, self.notFound])

    def testWord(self, word):
        if not self.correct.match(word): return False
        if not self.notFound.match(word): return False
        if not self.elsewhere.match(word): return False

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

        # print(f"Guessing {guess}")

        eliminations = lenWords*1.0
        for word in words:
            if word == guess: continue
            newClues = Clues.fromGuess(guess, word)
            clues = self.combine(newClues)
            count = clues.countWords(words)
            # print(f"If the word is {word}, we get {newClues} with {count} matches")
            eliminations -= count/lenWords
        return eliminations/lenWords

    def combine(self, clues):
        return Clues.makeClues(
            self.correct.combine(clues.correct), 
            self.elsewhere.combine(clues.elsewhere), 
            self.notFound.combine(clues.notFound),
        ) 

    @staticmethod
    def fromGuess(guess: str, actual: str):
        return Clues.makeClues(
            CorrectClue.fromGuess(guess, actual), 
            ElsewhereClue.fromGuess(guess, actual), 
            NotFoundClue.fromGuess(guess, actual),
        ) 

    def __hash__(self):
        return hash(str(self))
    
    def __eq__(self, o: object) -> bool:
        return str(self) == str(o)
    
def main(argv=sys.argv):
    ### DEBUG
    # argv = [ None, '.....', '////', '' ]
    # argv = [ None, '.....', 'd/o/u/l/', 'taresiy' ]
    # argv = [ None, '...e.', '//r//', 'tas' ]
    # argv = [ None, '.o.e.', 'd//r//', 'tasily' ]  ## Suspicious answer
    # argv = [ None, '.o.ed', 'd//r//', 'tasilybp' ]
    ### DEBUG

    allWords = readWords()
    clues = Clues.makeClues(
        CorrectClue.parse(argv[1]),
        ElsewhereClue.parse(argv[2]),
        NotFoundClue.parse(argv[3]),
    )

    possibilities = len(clues.getWords(allWords))

    print ("Wordl Guesser")
    print (f"Clues: {clues}")
    print(f"There are {possibilities} possibilities left")

    if possibilities <= 10:
        for word in clues.getWords(allWords): print(word)
    if possibilities <= 2:
        return 0

    bestGuess = ""
    bestValue = 0
    startTime = time.process_time()
    currentTime = startTime
    count = 0

    words = clues.getWords(allWords)
    for guess in allWords:
    # for guess in ['biped', 'aloes', 'tares', 'doily']:
        value = clues.valueOfGuess(guess, words)

        count += 1
        currentTime = time.process_time()
        totalTime = currentTime - startTime
        if theTimeLimit is not None and totalTime > theTimeLimit: return 1

        if value < bestValue: continue
        if value == bestValue and guess not in words and bestGuess in words: continue

        print(f"...Found {guess}:{value:.1%} ({totalTime:.0f}/{totalTime*len(allWords)/count:.0f} seconds)")
        bestGuess = guess
        bestValue = value


    print(f"If you guess '{bestGuess}' you'll eliminate an average of {bestValue:.1%}. ({totalTime:.1f} seconds)")

    return 0

if __name__ == "__main__":
    sys.exit(main())
