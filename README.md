# Guessl

This is a simple python script to play [Wordle](https://www.powerlanguage.co.uk/wordle/) or [Wordl](http://foldr.moe/hello-wordl/) so you don't have to.

It uses a word dictionary and the clues so far to determine what words are still possible, and, more
importantly, what guess will (on average) pare down the remaining possibilities the fastest.

NOTE: At the moment this only does 5-letter Wordl's.

# How To Use

Guessl uses a compact but weird syntax.  It's a command-line script that takes three arguments, in order:

For example: `./guess.py '...e.' '//r//' 'tasdoily'`

## 1. Correctly placed letters

For each of the five letter positions, a lower-case letter indicates the correct letter is in that position.  A dot ('.') indicates you don't know what goes there yet.

Example: `'...e.'` - The second to last letter is an "e".

## 2. Letters elsewhere in the word

For each letter position, you may have guessed some letters which are in the word, but not in the correct position.  You don't know where these letters go.  You do know they're in the word.  You *also* know they're not in the position where you guessed them.  This argument is described with the lower-case letters that are "elsewhere", separated by slashes ("/").

Example: `'//r//'` - There's an "r" in the word, but it's not the middle letter.

Example: `'a//ra//'` - There's an "a" and an "r" in the word.  "r" is not the middle letter. "a" is not the first or the middle letter.

## 3. Letters not found in the word

This is just a list of letters not in the word.

Example: `'tas'` - None of the letters "t", "a", or "s" are in the word.

# Example

    $ ./guess.py '...e.' '//r//' 'tasdoily'
    Wordl Guesser
    Clues: '...e.' '//r//' 'tasdoily'
    There are 19 possibilities left
    If you guess 'bench' you'll eliminate 87.5%. (2.1 seconds)

# Hint

Two of the best first guesses are "tares" and "aloes".  A great second word guess is "doily".
