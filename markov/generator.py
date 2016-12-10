#!/usr/bin/env python

"""
Example usage:

generator.py -i output.pkl -o markov_war_and_peace.txt

"""

import argparse
import logging
import pickle
import sys
import random
from utils import TokenMap, Arc
from collections import deque

logging.getLogger(__name__)

PROGRAM_NAME = 'generator'
PROGRAM_VERSION = '1.0'

class TokenStore:
    def __init__(self):
        self._toks= list()

    def __len__(self):
        return len(self._toks)

    def write(self, tok):
        self._toks.append(tok)

    def read(self):
        for tok in self._toks:
            yield tok

class TokenGenerator:
    _inputfile = ''

    def __init__(self, inputfile, n, length, quiet=False):
        self._inputfile = inputfile
        assert self._inputfile, "Input file must be provided."
        self._ngramsize = n
        assert self._ngramsize > 0, "ngramsize must be positive."
        self._length = length
        assert self._length > 0, "Lenth must be positive."

        if self._inputfile == '-':
            logging.info("Generate {} tokens from stdin.".format(self._length))
        else:
            logging.info("Generate {} tokens from file '{}'.".format(self._length, self._inputfile))

        self._quiet = quiet
        self._store = TokenStore()

        with open(self._inputfile) as inFile:
            self._tokenMap = pickle.load(inFile)

        self._generateTokens()

    def _tokenGenerator(self):
        currentToks = deque('')
        for _ in range(self._length):
            ilabel = " ".join(currentToks)
            arcs = self._tokenMap.getArcs(ilabel)
            if arcs:
                nextTok = random.choice(arcs).olabel
                yield nextTok
                currentToks.append(nextTok)
                if len(currentToks) > self._ngramsize:
                    currentToks.popleft()
            else:
                logging.warn("No acive tokens for '{}'".format(ilabel))

    def _generateTokens(self):
        generated = 0
        for tok in self._tokenGenerator():
            self._store.write(tok)
            generated += 1
            self._printCount(generated)
        self._endCountPrinting(generated)

    def _printCount(self, count):
        """
        Overwrite the line and reprint the message to prevent stdout spam.
        """
        if not self._quiet and count == 0:
            sys.stdout.write('\rToks generated: {} '.format(count))
            sys.stdout.flush()

    def _endCountPrinting(self, count):
        """
        Write out newline to move past the progress printer and log the total
        number of ngrams collected.
        """
        if not self._quiet:
            sys.stdout.write('\n')
            sys.stdout.flush()
        logging.info("Generated {} tokens.".format(count))

    def write(self, outputfile):
        outputfile.write(" ".join(self._store.read()))

    def _printProgress(self, progress):
        """
        Overwrite the line and reprint the message to prevent stdout spam.
        """
        if not self._quiet:
            sys.stdout.write('\rWriting store to CSV: [{0:50s}] {1:.2f}% '.format('#' * int(progress * 50.0), progress * 100.0))
            sys.stdout.flush()

    def _endProgressPrinting(self, nummetrics):
        """
        Write out newline to move past the progress printer and log the total
        number of metrics collected.
        """
        if not self._quiet:
            sys.stdout.write('\n')
            sys.stdout.flush()
        logging.info("Wrote metrics for {} requests to CSV.".format(nummetrics))


def main(argv):
    parser = argparse.ArgumentParser(prog='{}'.format(PROGRAM_NAME), description='Parse text corpra into n-gram model.')
    parser.add_argument('-v', '--version', action='version', version='{} {}'.format(PROGRAM_NAME, PROGRAM_VERSION))
    parser.add_argument('-i', '--infile', action='store', type=str, required=True, help='the input file, set to \'-\' for stdin.')
    parser.add_argument('-o', '--outfile', action='store', type=argparse.FileType('w'), required=True, help='the output destination')
    parser.add_argument('-n', '--ngramsize', action='store', type=int, help='the ngram size to parse', default=2)
    parser.add_argument('-t', '--length', action='store', type=int, help='the number of tokens to generate', default=200)
    parser.add_argument('-l', '--loglevel', action='store', type=str, help='log level to use', default='WARNING', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])

    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)

    generator = TokenGenerator(args.infile, args.ngramsize, args.length)
    generator.write(args.outfile)

if __name__ == "__main__":
    main(sys.argv[1:])
