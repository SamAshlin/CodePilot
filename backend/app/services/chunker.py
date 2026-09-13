from tree_sitter import Language, Parser

import tree_sitter_python
import tree_sitter_javascript
import tree_sitter_typescript


LANGUAGE_MAP = {
    "python": tree_sitter_python.language,
    "javascript": tree_sitter_javascript.language,
    "typescript": tree_sitter_typescript.language_typescript,
}


# Nodes that represent meaningful code units.
CODE_UNIT_TYPES = {
    "python": {
        "function_definition",
        "class_definition",
    },

    "javascript": {
        "function_declaration",
        "class_declaration",
        "method_definition",
        "arrow_function",
    },

    "typescript": {
        "function_declaration",
        "class_declaration",
        "method_definition",
        "arrow_function",
    }
}


def get_parser(language):

    if language not in LANGUAGE_MAP:
        return None

    parser = Parser()

    language_object = Language(
        LANGUAGE_MAP[language]()
    )

    parser.language = language_object

    return parser


def parse_file(content, language):

    parser = get_parser(language)

    if parser is None:
        return None

    return parser.parse(
        content.encode("utf-8")
    )


def get_parent_class(context):

    for item in context:

        if item.startswith("class:"):
            return item.split(
                "class:",
                1
            )[1]

    return None

def get_class_header(node, content):

    lines = content[
        node.start_byte:node.end_byte
    ].splitlines()

    if not lines:
        return ""

    # For the MVP, the first line represents
    # the class declaration.
    return lines[0]

def get_header_end_line(node, content):

    return node.start_point[0] + 1

def extract_code_units(
    node,
    language,
    content,
    parent_context=None
):
    units = []

    if parent_context is None:
        parent_context = []

    target_types = CODE_UNIT_TYPES.get(
        language,
        set()
    )

    current_context = parent_context.copy()

    # -----------------------------------------
    # CLASS
    # -----------------------------------------

    if node.type in {
        "class_definition",
        "class_declaration"
    }:

        name = get_node_name(node)

        if name:
            current_context.append(
                f"class:{name}"
            )

        # Create a class chunk only for the
        # class declaration/header.
        class_header = get_class_header(
            node,
            content
        )

        if class_header:

            units.append({
                "content": class_header,
                "file_path": None,
                "language": language,
                "start_line": node.start_point[0] + 1,
                "end_line": get_header_end_line(
                    node,
                    content
                ),
                "chunk_type": "class",
                "name": name,
                "parent": None,
                "context": current_context.copy()
            })

        # Continue inside the class so that
        # methods become individual chunks.
        for child in node.children:

            units.extend(
                extract_code_units(
                    child,
                    language,
                    content,
                    current_context
                )
            )

        return units

    # -----------------------------------------
    # FUNCTION / METHOD
    # -----------------------------------------

    if node.type in target_types:

        name = get_node_name(node)

        function_context = current_context.copy()

        if name:
            function_context.append(
                f"method:{name}"
            )

        code = content[
            node.start_byte:node.end_byte
        ]

        units.append({
            "content": code,
            "file_path": None,
            "language": language,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "chunk_type": (
                "method"
                if parent_context
                else "function"
            ),
            "name": name,
            "parent": get_parent_class(
                current_context
            ),
            "context": function_context
        })

        return units

    # -----------------------------------------
    # OTHER NODES
    # -----------------------------------------

    for child in node.children:

        units.extend(
            extract_code_units(
                child,
                language,
                content,
                current_context
            )
        )

    return units


def get_node_name(node):

    # Common Tree-sitter pattern:
    #
    # class_definition
    # ├── name
    #
    # function_definition
    # ├── name

    for child in node.children:

        if child.type == "identifier":

            return child.text.decode(
                "utf-8"
            )

    return None


def fallback_chunk(
    content,
    file_path,
    language,
    chunk_size=100,
    overlap=20
):

    lines = content.splitlines()

    chunks = []

    start = 0

    while start < len(lines):

        end = min(
            start + chunk_size,
            len(lines)
        )

        text = "\n".join(
            lines[start:end]
        )

        if text.strip():

            chunks.append({
                "content": text,
                "file_path": file_path,
                "language": language,
                "start_line": start + 1,
                "end_line": end,
                "chunk_type": "text",
                "name": None,
                "context": []
            })

        start = end - overlap

        if start <= 0:
            start = end

    return chunks


def chunk_code(
    content,
    file_path,
    language,
    chunk_size=100,
    overlap=20
):

    tree = parse_file(
        content,
        language
    )

    # Unsupported language
    if tree is None:

        return fallback_chunk(
            content,
            file_path,
            language,
            chunk_size,
            overlap
        )

    units = extract_code_units(
        tree.root_node,
        language,
        content
    )

    # No AST units found
    if not units:

        return fallback_chunk(
            content,
            file_path,
            language,
            chunk_size,
            overlap
        )

    chunks = []

    for unit in units:

        unit["file_path"] = file_path

        chunks.append(unit)

    return chunks