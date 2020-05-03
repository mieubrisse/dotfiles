import os
from collections import defaultdict
import datetime

# Keys for the dict of file + metadata we pass around
class EntryAndMetadata:
    """
    Class to contain information about a journal entry - filename on disk, date of creation, tags, etc.
    """

    MISSING_DATE_FORMAT_DATE = datetime.datetime(1970, 1, 1, 0, 0, 0)    # Date we assume an entry was written if we can't parse the date
    FILENAME_DATE_FMTS = [
        "%Y-%m-%d_%H-%M-%S",
        "%Y-%m-%d"
    ]

    def __init__(self, filename):
        filename_minus_ext, extension = os.path.splitext(filename)

        filename_fragments = filename_minus_ext.split("~")
        self.pseudo_name = filename_fragments[0] + extension
        created_timestamp_str = filename_fragments[1] if len(filename_fragments) >= 2 else ""
        tags_str = filename_fragments[2] if len(filename_fragments) >= 3 else ""

        self.creation_timestamp = EntryAndMetadata.MISSING_DATE_FORMAT_DATE
        for date_format in EntryAndMetadata.FILENAME_DATE_FMTS:
            try:
                self.creation_timestamp = datetime.datetime.strptime(created_timestamp_str, date_format)
                break
            except ValueError:
                pass
        self.tags = tags_str.split(",") if len(tags_str) > 0 else []

    def __repr__(self):
        return self.filename

    def __str__(self):
        tag_str = "   \033[35m%s" % " ".join(sorted(self.tags)) if len(self.tags) > 0 else ""
        return "\033[33m%s   \033[37m%s%s\033[39;49m" % (self.creation_timestamp, self.pseudo_name, tag_str)


class EntryStore:
    """
    Takes a list of EntryAndMetadata and processes it in an easily-queryable format
    """

    def __init__(self, entry_list):
        self._entries = set(entry_list)
        self._tag_lookup = defaultdict(lambda: set())
        for entry in self._entries:
            for tag in entry.tags:
                self._tag_lookup[tag].add(entry)

    def get_all(self):
        return self._entries

    def get_tags(self):
        return self._tag_lookup.keys()

    def get_by_tag(self, tag):
        return self._tag_lookup.get(tag, set())

    def get_by_name(self, keyword):
        return [ entry for entry in self._entries if keyword in entry.pseudo_name]
