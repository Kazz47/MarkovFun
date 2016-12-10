from collections import namedtuple

Arc = namedtuple('Arc', ['ilabel', 'olabel', 'weight'])

class TokenMap:
    def __init__(self, ngramMap=dict()):
        self._map = dict()

        try:
            for key, value in ngramMap:
                newArc = Arc(ilabel=key[0], olabel=key[1], weight=value)
                if (newArc.ilabel in self._map):
                    self._map[newArc.ilabel].append(newArc)
                else:
                    self._map[newArc.ilabel] = [newArc]
        except TypeError:
            print ngramMap, 'is not iterable'

        # Normalize?

    def __len__(self):
        return len(self._map)

    def getArcs(self, ilabel):
        return self._map.get(ilabel, [])
