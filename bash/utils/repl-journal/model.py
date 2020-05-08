import os
from collections import defaultdict
import datetime

# Keys for the dict of file + metadata we pass around
class _EntryStoreRecord:
    """
    Class to contain information about a journal entry - filename on disk, date of creation, tags, etc.
    """


    def __init__(self, filename):
        filename_minus_ext, extension = os.path.splitext(filename)

        filename_fragments = filename_minus_ext.split("~")
        self._pseudo_name = filename_fragments[0] + extension
        created_timestamp_str = filename_fragments[1] if len(filename_fragments) >= 2 else ""
        tags_str = filename_fragments[2] if len(filename_fragments) >= 3 else ""

        self._filename = filename
        self._creation_timestamp = EntryAndMetadata.MISSING_DATE_FORMAT_DATE
        for date_format in EntryAndMetadata.FILENAME_DATE_FMTS:
            try:
                self._creation_timestamp = datetime.datetime.strptime(created_timestamp_str, date_format)
                break
            except ValueError:
                pass
        self._tags = tags_str.split(",") if len(tags_str) > 0 else []

    def get_id(self):
        return self._filename

    def __repr__(self):
        return self.get_id()

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

    def get_entry_id(self):
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

    def 

class EntryStore:
    """
    Takes a list of EntryAndMetadata and processes it in an easily-queryable format
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

        self._entries = set(journal_filenames)
        self._tag_lookup = defaultdict(lambda: set())
        for entry in self._entries:
            for tag in entry.tags:
                self._tag_lookup[tag].add(entry)



        self._filename = filename

        entries = [ model.EntryStoreRecord(filename) for filename in journal_filenames]

        self._entries = set(entry_list)
        self._tag_lookup = defaultdict(lambda: set())
        for entry in self._entries:
            for tag in entry.tags:
                self._tag_lookup[tag].add(entry)

    def get_all(self):
        return self._entries

    def get_tags(self):
        return self._tag_lookup.keys()

    def get_by_id(self, entry_id):
        return self._entries.get(entry_id, None)

    def get_by_tag(self, tag):
        return self._tag_lookup.get(tag, set())

    def get_by_name(self, keyword):
        return [ entry for entry in self._entries if keyword in entry.pseudo_name]

    """
    def _to_api_entry(self, entry_record):
        Helper function to convert the internal entries to external objects returned to the user
        return Entry(
    """

    def _get_metadata_from_filename(filename):
        """
        Splits a metadata-bearing filename into the pseudo filename (without metadata), creation timestamp, and tags

        Returns:
            Tuple containing (pseudo_name, creation_timestamp, tags)
        """
        filename_minus_ext, extension = os.path.splitext(filename)
        filename_fragments = filename_minus_ext.split(EntryStore._FILENAME_METADATA_SEPARATOR)

        pseudo_name = filename_fragments[0] + extension

        created_timestamp_str = filename_fragments[1] if len(filename_fragments) >= 2 else ""
        creation_timestamp = EntryStore._MISSING_DATE_FORMAT_DATE
        for date_format in EntryStore._FILENAME_DATE_FMTS:
            try:
                self._creation_timestamp = datetime.datetime.strptime(created_timestamp_str, date_format)
                break
            except ValueError:
                pass

        tags_str = filename_fragments[2] if len(filename_fragments) >= 3 else ""
        tags_list = tags_str.split(",") if len(tags_str) > 0 else []
        return (pseudo_name, creation_timestamp, 


    def _is_valid_journal_entry(journal_dirpath, filename, compiled_blacklisted_patterns):
        result = os.path.isfile(os.path.join(journal_dirpath, filename))
        for pattern in compiled_blacklisted_patterns:
            return result and not pattern.match(filename)
        return result
