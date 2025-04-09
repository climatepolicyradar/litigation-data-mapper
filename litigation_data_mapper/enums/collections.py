from enum import Enum


class RequiredCollectionKeys(Enum):
    """The keys the data mapper needs to parse collections data / metadata"""

    BUNDLE_ID = "id"
    TITLE = "title"
    DESCRIPTION = "ccl_core_object"
