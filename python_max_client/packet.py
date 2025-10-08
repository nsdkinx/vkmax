from dataclasses import dataclass
from typing import Literal, Any


@dataclass
class MaxPacket:
    # Not used anywhere, but that's going to change soon
    ver: int
    cmd: Literal[0, 1]
    opcode: int
    seq: int
    payload: dict[str, Any]
