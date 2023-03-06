from _typeshed import Incomplete

TAR_HEADER: Incomplete
DIRTYPE: str
REGTYPE: str

def roundup(val, align): ...

class FileSection:
    f: Incomplete
    content_len: Incomplete
    align: Incomplete
    def __init__(self, f, content_len, aligned_len) -> None: ...
    def read(self, sz: int = ...): ...
    def readinto(self, buf): ...
    def skip(self) -> None: ...

class TarInfo:
    def __str__(self): ...

class TarFile:
    f: Incomplete
    subf: Incomplete
    def __init__(self, name: Incomplete | None = ..., fileobj: Incomplete | None = ...) -> None: ...
    def next(self): ...
    def __iter__(self): ...
    def __next__(self): ...
    def extractfile(self, tarinfo): ...
