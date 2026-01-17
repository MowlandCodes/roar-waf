import re
from collections import deque
from typing import IO, Deque, Generator
from urllib import parse

from libs import db
from libs.logger import logger
from models.logs import AttackLog
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
        extension = stream.read(MAX_EXTEND)

        if extension:
            found_idx = -1
            for i, byte in enumerate(extension):
                if byte in DELIMITERS:
                    found_idx = i
                    break

            if found_idx != -1:
                chunk += extension[:found_idx + 1]
            else:
                chunk += extension

    return chunk


def inspect_head_and_tail(stream: ByteStream, rules: list[Rule], hostname: str, remote_addr: str | None) -> Generator[bytes, None, None]:
    """
    Inspect the head and the tail of the `stream` with the given `rules`
    """
    head_chunk = read_head(stream)

    head_text = head_chunk.decode('utf-8', errors='ignore')

    for rule in rules:
        if re.search(str(rule.pattern), head_text):
            logger.info(f"BLOCKED : {str(rule.name)} rule triggered")
            attack_log = AttackLog(
                src_ip=remote_addr or "unknown",
                target_domain=hostname, 
                matched_rule=str(rule.name), 
                payload_sample=head_text
            )

            db.session.add(attack_log)
            db.session.commit()

            raise Exception(f"BLOCKED : {str(rule.name)} rule triggered")

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
                logger.info(f"BLOCKED : {str(rule.name)} rule triggered")
                attack_log = AttackLog(
                    src_ip=remote_addr or "unknown",
                    target_domain=hostname, 
                    matched_rule=str(rule.name), 
                    payload_sample=tail_text
                )

                db.session.add(attack_log)
                db.session.commit()
                raise Exception(f"BLOCKED : {str(rule.name)} rule triggered")


def inspect_url(url:str, rules: list[Rule], hostname: str, remote_addr: str | None):
    parsed_url = parse.unquote_plus(url)

    for rule in rules:
        if re.search(str(rule.pattern), parsed_url):
            logger.info(f"BLOCKED : {str(rule.name)} rule triggered")
            attack_log = AttackLog(
                src_ip=remote_addr or "unknown",
                target_domain=hostname, 
                matched_rule=str(rule.name), 
                payload_sample=parsed_url
            )

            db.session.add(attack_log)
            db.session.commit()

            raise Exception(f"BLOCKED : {str(rule.name)} rule triggered")
