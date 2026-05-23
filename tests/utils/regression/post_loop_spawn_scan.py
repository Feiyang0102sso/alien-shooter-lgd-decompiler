"""
post_loop_spawn_scan.py

Scan decompiled LGC for the do-while dual-exit / post-loop spawn regression profile.

Bug (survive mod not spawn): after while(1)+break placement loop, decompiler emitted
only ``return;`` and dropped CreateSprite / Action. Also ``attemps==max`` was ``break``.
"""

import re
from dataclasses import dataclass
from pathlib import Path


TARGET_FUNCTION = "monstersCreationTact"


@dataclass
class PostLoopSpawnScanResult:
    """Outcome of scanning one LGC file for post-loop spawn preservation."""

    function_body: str
    has_while_one: bool
    has_create_sprite_after_loop: bool
    has_action_after_loop: bool
    max_attemps_uses_return: bool
    max_attemps_uses_break: bool
    has_bare_return_after_loop: bool


def extract_function_body(lgc_text: str, function_name: str) -> str:
    """
    Extract the body of ``function_name(...) { ... }`` from full LGC source.

    Returns empty string if the function is not found.
    """
    marker = function_name + "("
    start = lgc_text.find(marker)
    if start < 0:
        return ""

    brace_start = lgc_text.find("{", start)
    if brace_start < 0:
        return ""

    depth = 0
    index = brace_start
    while index < len(lgc_text):
        char = lgc_text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return lgc_text[start : index + 1]
        index += 1

    return ""


def _find_matching_brace(text: str, open_brace_index: int) -> int:
    """Return index of ``}`` matching ``{`` at ``open_brace_index``, or -1."""
    depth = 0
    index = open_brace_index
    while index < len(text):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return -1


def _text_after_while_one_loop(function_body: str) -> str:
    """
    Return text after the closing ``}`` of the first ``while (1)`` in ``function_body``.
    """
    while_index = function_body.find("while (1)")
    if while_index < 0:
        return ""

    open_brace = function_body.find("{", while_index)
    if open_brace < 0:
        return ""

    close_brace = _find_matching_brace(function_body, open_brace)
    if close_brace < 0:
        return ""

    return function_body[close_brace + 1 :]


def _while_one_loop_body(function_body: str) -> str:
    """Return the full ``while (1) { ... }`` substring, or empty string."""
    while_index = function_body.find("while (1)")
    if while_index < 0:
        return ""

    open_brace = function_body.find("{", while_index)
    if open_brace < 0:
        return ""

    close_brace = _find_matching_brace(function_body, open_brace)
    if close_brace < 0:
        return ""

    return function_body[while_index : close_brace + 1]


def scan_post_loop_spawn(lgc_text: str, function_name: str = TARGET_FUNCTION) -> PostLoopSpawnScanResult:
    """
    Scan ``lgc_text`` for post-loop spawn profile inside ``function_name``.
    """
    function_body = extract_function_body(lgc_text, function_name)
    if not function_body:
        return PostLoopSpawnScanResult(
            function_body="",
            has_while_one=False,
            has_create_sprite_after_loop=False,
            has_action_after_loop=False,
            max_attemps_uses_return=False,
            max_attemps_uses_break=False,
            has_bare_return_after_loop=False,
        )

    loop_body = _while_one_loop_body(function_body)
    after_loop = _text_after_while_one_loop(function_body)

    has_while_one = bool(loop_body)
    has_create_sprite_after_loop = "CreateSprite" in after_loop
    has_action_after_loop = "Action(" in after_loop

    # attemps==max: fixed decompile uses return inside while(1), legacy bug used break
    max_return_pattern = re.compile(
        r"if \(\([^)]*_local24 == [^)]*_local23\)\) \{\s*return;",
        re.MULTILINE,
    )
    max_break_pattern = re.compile(
        r"if \(\([^)]*_local24 == [^)]*_local23\)\) \{\s*break;",
        re.MULTILINE,
    )

    max_attemps_uses_return = bool(max_return_pattern.search(loop_body))
    max_attemps_uses_break = bool(max_break_pattern.search(loop_body))

    # Legacy bug: immediately ``return;`` after loop with no CreateSprite in between
    stripped = after_loop.strip()
    has_bare_return_after_loop = False
    if stripped.startswith("return"):
        has_bare_return_after_loop = True
    elif re.match(r"return;\s*(//|$)", stripped):
        has_bare_return_after_loop = True

    return PostLoopSpawnScanResult(
        function_body=function_body,
        has_while_one=has_while_one,
        has_create_sprite_after_loop=has_create_sprite_after_loop,
        has_action_after_loop=has_action_after_loop,
        max_attemps_uses_return=max_attemps_uses_return,
        max_attemps_uses_break=max_attemps_uses_break,
        has_bare_return_after_loop=has_bare_return_after_loop,
    )


def scan_lgc_file(lgc_path: Path, function_name: str = TARGET_FUNCTION) -> PostLoopSpawnScanResult:
    """Load LGC from disk and run :func:`scan_post_loop_spawn`."""
    text = lgc_path.read_text(encoding="utf-8")
    return scan_post_loop_spawn(text, function_name=function_name)


def looks_like_legacy_post_loop_bug(result: PostLoopSpawnScanResult) -> bool:
    """
    True when output matches the pre-fix failure mode (post-loop spawn lost).
    """
    if not result.has_while_one:
        return False

    spawn_lost = not result.has_create_sprite_after_loop or not result.has_action_after_loop
    if spawn_lost:
        return True

    if result.has_bare_return_after_loop:
        return True

    if result.max_attemps_uses_break and not result.max_attemps_uses_return:
        return True

    return False


def looks_like_fixed_post_loop(result: PostLoopSpawnScanResult) -> bool:
    """True when output matches the expected fixed decompile profile."""
    if not result.has_while_one:
        return False

    if not result.has_create_sprite_after_loop:
        return False

    if not result.has_action_after_loop:
        return False

    if result.has_bare_return_after_loop:
        return False

    if result.max_attemps_uses_break:
        return False

    if not result.max_attemps_uses_return:
        return False

    return True
