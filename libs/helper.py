import re
from collections import deque
from typing import IO, Deque, Generator

from models.rules import Rule

HEAD_SIZE = 1024 * 8 # 8kb
TAIL_SIZE = 1024 * 8
MAX_EXTEND = 512

DELIMITERS = b' \n\r\t>;,("\''

ByteStream = IO[bytes]


def read_head(stream: ByteStream) -> bytes:
    """
    Reads the first `HEAD_SIZE` bytes from the stream,
    extends the stream if needed until one of `DELIMITERS` is found
    """

    chunk = stream.read(HEAD_SIZE)

    if not chunk:
        return b''

    # Return if chunk is less than HEAD_SIZE (stream is less than HEAD_SIZE / Short Stream)
    if len(chunk) < HEAD_SIZE:
        return chunk

    # Read the last bytes
    last_byte = chunk[-1:]

    if last_byte not in DELIMITERS:
        extension = b""

        for _ in range(MAX_EXTEND):
            char = stream.read(1)

            if not char:
                break

            extension += char

            if char in DELIMITERS:
                break

        chunk += extension

    return chunk


def inspect_head_and_tail(stream: ByteStream, rules: list[Rule]) -> Generator[bytes, None, None]:
    """
    Inspect the head and the tail of the `stream` with the given `rules`
    """
    head_chunk = read_head(stream)

    head_text = head_chunk.decode('utf-8', errors='ignore')

    for rule in rules:
        if re.search(str(rule.pattern), head_text):
            raise Exception(f"{str(rule.name)} rule triggered")

    yield head_chunk


    tail_buffer: Deque[int] = deque(maxlen=TAIL_SIZE)

    while True:
        chunk: bytes = stream.read(4096) # Read 4kb at a time

        if not chunk:
            break

        tail_buffer.extend(chunk)
        yield chunk


    if tail_buffer:
        tail_data: bytes = bytes(tail_buffer)
        tail_text: str = tail_data.decode('utf-8', errors='ignore')

        for rule in rules:
            if re.search(str(rule.pattern), tail_text):
                raise Exception(f"{str(rule.name)} rule triggered")
