"""hash_table.py - a hash table using OPEN ADDRESSING with LINEAR PROBING.

This file contains no pharmacy code, so the same class can store any key/value pairs.

How the table works
-------------------
* self.table is a list of `size` slots. Each slot is in exactly one of three states:
      None      -> EMPTY     never used. An empty slot ends every search.
      DELETED   -> DELETED   a "tombstone" left behind by delete().
      Slot      -> OCCUPIED  holds one key and its value.
* Hash function (same as the practicals):
      integer key -> key % size
      string key  -> (sum of the ASCII codes of its characters) % size
* Collision (linear probing): if the home slot is taken, try home+1, home+2, ...
  and wrap round to slot 0 after the last slot.
* delete() leaves a tombstone. Emptying the slot would cut the probe chain of the
  keys that were pushed past it and make them impossible to find.
* When the table is more than max_load_factor full, it is rebuilt (rehashed):
  bigger if it is really crowded, the same size if the crowding is only tombstones.
"""

DELETED = "<deleted>"           # tombstone marker, always compared with `is`
GROWTH_FACTOR = 2               # a crowded table grows to the next prime >= GROWTH_FACTOR x size

# Slot states reported by slot_view()
STATE_EMPTY = "EMPTY"
STATE_DELETED = "DELETED"
STATE_OCCUPIED = "OCCUPIED"


class DuplicateKeyError(Exception):
    """Raised when inserting a key that is already in the table."""


class HashTableFullError(Exception):
    """Raised when no slot is free (only possible when auto_resize is False)."""


class Slot:
    """One occupied slot of the table: a key together with its value."""

    def __init__(self, key, value):
        self.key = key
        self.value = value


def is_prime(number):
    """True if `number` is a prime number."""
    if number < 2:
        return False
    divisor = 2
    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor += 1
    return True


def next_prime(number):
    """Smallest prime number that is >= `number`."""
    while not is_prime(number):
        number += 1
    return number


class HashTable:
    """Hash table with open addressing and linear probing."""

    def __init__(self, size=11, max_load_factor=0.7, auto_resize=True):
        if size < 1:
            raise ValueError("size must be at least 1")
        if not 0 < max_load_factor < 1:
            raise ValueError("max_load_factor must be between 0 and 1 (exclusive)")
        self.size = size                    # number of slots
        self.table = [None] * size          # the slots themselves
        self.count = 0                      # slots holding a live record
        self.tombstones = 0                 # slots holding a tombstone
        self.max_load_factor = max_load_factor
        self.auto_resize = auto_resize
        self.last_probes = 0                # slots examined by the latest operation
        self.resize_count = 0               # how many times the table was rehashed

    # ------------------------------------------------------------------ hashing
    def hash_function(self, key):
        """Return the home slot of `key`, where its probe sequence starts."""
        if isinstance(key, str):
            return sum(ord(char) for char in key) % self.size
        if isinstance(key, int):
            return key % self.size
        return hash(key) % self.size        # any other hashable type

    # ------------------------------------------------------------------ core operations
    def insert(self, key, value):
        """Store (key, value) and return the index of the slot used.

        Raises DuplicateKeyError if the key is already in the table.
        """
        used = self.count + self.tombstones         # live records + tombstones
        if self.auto_resize and used + 1 > self.max_load_factor * self.size:
            self.rehash()

        index = self.hash_function(key)
        first_deleted = -1          # first tombstone met on the way; it can be reused
        found_empty = False
        probes = 0

        while probes < self.size:
            slot = self.table[index]
            probes += 1
            if slot is None:                        # empty: the key is not in the table
                found_empty = True
                break
            if slot is DELETED:
                if first_deleted < 0:
                    first_deleted = index
            elif slot.key == key:                   # scan the whole chain for duplicates
                self.last_probes = probes
                raise DuplicateKeyError(key)
            index = (index + 1) % self.size         # linear probing step, wraps to 0
        self.last_probes = probes

        if first_deleted >= 0:                      # prefer to recycle a tombstone
            target = first_deleted
            self.tombstones -= 1
        elif found_empty:
            target = index
        else:
            raise HashTableFullError("no free slot available")

        self.table[target] = Slot(key, value)
        self.count += 1
        return target
    
    def find_index(self, key):
        """Return the slot index that holds `key`, or -1. Also sets last_probes."""
        index = self.hash_function(key)
        probes = 0
        while probes < self.size:
            slot = self.table[index]
            probes += 1
            if slot is None:                        # an empty slot ends the search
                break
            if slot is not DELETED and slot.key == key:
                self.last_probes = probes
                return index
            index = (index + 1) % self.size         # a tombstone does NOT end the search
        self.last_probes = probes
        return -1
    
    def delete(self, key):
        """Remove `key` and leave a tombstone. Returns False if the key is absent."""
        index = self.find_index(key)
        if index < 0:
            return False
        self.table[index] = DELETED
        self.count -= 1
        self.tombstones += 1
        return True

    def rehash(self):
        """Rebuild the table, dropping every tombstone.

        If the live records alone fill more than half of the allowed load, the table
        grows to the next prime >= GROWTH_FACTOR x size. Otherwise the crowding is mostly
        tombstones, so it is rebuilt at the same size (otherwise repeated insert and
        delete would make an almost empty table grow for ever).
        """
        if self.count + 1 > self.max_load_factor * self.size / 2:
            new_size = next_prime(GROWTH_FACTOR * self.size)
        else:
            new_size = self.size

        old_table = self.table
        self.size = new_size
        self.table = [None] * new_size
        self.count = 0
        self.tombstones = 0
        for slot in old_table:
            if slot is not None and slot is not DELETED:
                index = self.hash_function(slot.key)        # uses the NEW size
                while self.table[index] is not None:        # keys are unique here
                    index = (index + 1) % new_size
                self.table[index] = slot
                self.count += 1
        self.resize_count += 1

    def search(self, key, default=None):
        """Return the value stored for `key`, or `default` if it is not there."""
        index = self.find_index(key)
        if index < 0:
            return default
        return self.table[index].value

    def update(self, key, value):
        """Replace the value of an existing key. Returns False if the key is absent."""
        index = self.find_index(key)
        if index < 0:
            return False
        self.table[index].value = value
        return True

    # ------------------------------------------------------------------ information
    def load_factor(self):
        """Fraction of slots holding live records (n / m)."""
        return self.count / self.size

    def __len__(self):
        return self.count

    def __contains__(self, key):
        return self.find_index(key) >= 0

    def items(self):
        """List of every (key, value) pair, in slot order."""
        return [(slot.key, slot.value) for slot in self.table
                if slot is not None and slot is not DELETED]

    def slot_view(self):
        """List of (index, state, key, value) for every slot - used to display the table."""
        view = []
        for index, slot in enumerate(self.table):
            if slot is None:
                view.append((index, STATE_EMPTY, None, None))
            elif slot is DELETED:
                view.append((index, STATE_DELETED, None, None))
            else:
                view.append((index, STATE_OCCUPIED, slot.key, slot.value))
        return view
