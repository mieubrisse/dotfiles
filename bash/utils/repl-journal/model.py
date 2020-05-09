import os
from collections import defaultdict
import datetime
import re

# Keys for the dict of file + metadata we pass around
class EntryStoreRecord:
    """
    Class to contain information about a journal entry - filename on disk, date of creation, tags, etc.
    """

    _MISSING_DATE_FORMAT_DATE = datetime.datetime(1970, 1, 1, 0, 0, 0)    # Date we assume an entry was written if we can't parse the date
    _FILENAME_DATE_FMTS = [
        "%Y-%m-%d_%H-%M-%S",
        "%Y-%m-%d"
    ]

    def __init__(self, filename):
        self._filename = filename
        filename_minus_ext, extension = os.path.splitext(self._filename)
        filename_fragments = filename_minus_ext.split("~")

        self._pseudo_name = filename_fragments[0] + extension

        created_timestamp_str = filename_fragments[1] if len(filename_fragments) >= 2 else ""
        self._creation_timestamp = EntryStoreRecord._MISSING_DATE_FORMAT_DATE
        for date_format in EntryStoreRecord._FILENAME_DATE_FMTS:
            try:
                self._creation_timestamp = datetime.datetime.strptime(created_timestamp_str, date_format)
                break
            except ValueError:
                pass

        tags_str = filename_fragments[2] if len(filename_fragments) >= 3 else ""
        self._tags = tags_str.split(",") if len(tags_str) > 0 else []

    def get_filename(self):
        return self._filename

    def get_pseudo_name(self):
        return self._pseudo_name

    def get_creation_timestamp(self):
        return self._creation_timestamp

    def get_tags(self):
        return self._tags

    def __repr__(self):
        return self.get_filename()

# NOTE: this is the external representation, not how we store the data internal to the EntryStore
class Entry:
    """
    POPO representing journal entries stored in the EntryStore
    NOTE: These objects became outdated as soon as the EntryStore is modified!
    """
    def __init__(self, entry_id, filepath, creation_timestamp, name, tags):
        """
        Args:
            entry_id: The ID of this entry, which will be used to identify it with the EntryStore in the future
            filepath: Absolute path on the filesystem to this entry
            name: Name of this entry (which does NOT simply correspond to the filename)
            tags: Tags for this entry
        """
        self._entry_id = entry_id
        self._filepath = filepath
        self._creation_timestamp = creation_timestamp
        self._name = name
        self._tags = sorted(set(tags))

    def get_id(self):
        return self._entry_id

    def get_filepath(self):
        return self._filepath

    def get_creation_timestamp(self):
        return self._creation_timestamp

    def get_name(self):
        return self._name

    def get_tags(self):
        return self._tags

    def __str__(self):
        tag_str = "   \033[35m%s" % " ".join(self._tags) if len(self._tags) > 0 else ""
        return "\033[33m%s   \033[37m%s%s\033[39;49m" % (
            self._creation_timestamp,
            self._name,
            tag_str
        )

class EntryStore:
    """
    Takes a list of EntryStoreRecords and processes them into an easily-queryable format
    """

    _FILENAME_METADATA_SEPARATOR = "~"

    _MISSING_DATE_FORMAT_DATE = datetime.datetime(1970, 1, 1, 0, 0, 0)    # Date we assume an entry was written if we can't parse the date
    _FILENAME_DATE_FMTS = [
        "%Y-%m-%d_%H-%M-%S",
        "%Y-%m-%d"
    ]

    def __init__(self, journal_dirpath, blacklisted_patterns):
        """
        Args:
            journal_dirpath: Directory containing the journal entries
            blacklisted_pattens: List of uncompiled filename regexes to ignore (can be empty)
        """
        self._journal_dirpath = journal_dirpath
        self._compiled_blacklisted_patterns = [re.compile(pattern) for pattern in blacklisted_patterns]

        journal_filenames = [
            filename for filename in os.listdir(journal_dirpath)
            if EntryStore._is_valid_journal_entry(
                self._journal_dirpath,
                filename,
                self._compiled_blacklisted_patterns
            )
        ]
        records_set = { EntryStoreRecord(filename) for filename in journal_filenames }

        self._records = {}
        self._pseudo_name_index = {}
        self._tag_index = defaultdict(lambda: set())
        for record in records_set:
            record_filename = record.get_filename()
            self._records[record_filename] = record
            self._pseudo_name_index[record.get_pseudo_name()] = record_filename
            for tag in record.get_tags():
                self._tag_index[tag].add(record_filename)

    def get_all(self):
        return [self._record_to_entry(record) for record in self._records.values()]

    def get_tags(self):
        return self._tag_index.keys()

    def get_by_ids(self, the_ids):
        # NOTE: A nonexistent ID here will and should throw an error, because it means the user
        #  is passing in IDs other than the ones we're giving back!
        return [
            self._record_to_entry(self._records.get(record_id)) for record_id in the_ids
        ]

    def get_by_tag(self, tag):
        return [
            self._record_to_entry(self._records.get(record_id))
            for record_id
            in self._tag_index.get(tag, set())
        ]

    def get_by_name(self, keyword):
        return [
            self._record_to_entry(self._records.get(record_id))
            for pseudo_name, record_id
            in self._pseudo_name_index.items()
            if keyword in pseudo_name
        ]

    def _record_to_entry(self, record):
        """
        Helper function to convert from the internal entries representation to external objects returned to the user
        """
        filename = record.get_filename()
        return Entry(
            filename,
            os.path.join(self._journal_dirpath, filename),
            record.get_creation_timestamp(),
            record.get_pseudo_name(),
            record.get_tags()
        )

    def _is_valid_journal_entry(journal_dirpath, filename, compiled_blacklisted_patterns):
        result = os.path.isfile(os.path.join(journal_dirpath, filename))
        for pattern in compiled_blacklisted_patterns:
            return result and not pattern.match(filename)
        return result
