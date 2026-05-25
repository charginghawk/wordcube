"""
Run via:  Scripting > Run Script
"""

# TODO Figure out bolding (use TextPlus?).
# TODO Figure out sizing.
# TODO Scale font to sizing.

import math
import pymxs

rt = pymxs.runtime  # shorthand to the MAXScript runtime


# ── Word data ─────────────────────────────────────────────────────────────────

WORD_ARRAYS = [
    ["OSTLER", "SERENE", "TRYSTS", "LESSEE", "ENTERA", "RESEAL"],
    ["TERETE", "EMETIN", "RELENT", "ETERNE", "TINNER", "ENTERA"],
    ["SHOVEL", "HALITE", "OLIVES", "VIVERS", "ETERNE", "LESSEE"],
    ["ESCORT", "STALER", "CAGILY", "OLIVES", "RELENT", "TRYSTS"],
    ["RUSHES", "UNTAME", "STALER", "HALITE", "EMETIN", "SERENE"],
    ["PRESTO", "RUSHES", "ESCORT", "SHOVEL", "TERETE", "OSTLER"],
]

# ── Visual settings ───────────────────────────────────────────────────────────

# 3ds Max scene units are typically inches or cm; adjust as needed.
# Blender's default unit is metres; 0.25 m ≈ 25 scene units if units = cm.
FONT_SIZE       = 6.5   # text height in scene units
EXTRUDE_DEPTH   = 0.5   # extrusion depth (0 = flat spline, no geometry depth)
LETTER_ANGLE_X  = 45    # rotation around X axis, degrees
LETTER_ANGLE_Y  = 0     # rotation around Y axis, degrees
LETTER_ANGLE_Z  = -45   # rotation around Z axis, degrees
FONT            = 'Franklin Gothic Demi'
# Comic Sans MS, Verdana, Franklin Gothic Heavy/Demi/Medium/Book

# Spacing between letter columns / rows (scene units)
COLUMN_SPACING  = 30.0
ROW_SPACING     = 30.0
LAYER_SPACING   = 30.0   # Z offset per layer


# ── Helpers ───────────────────────────────────────────────────────────────────

def clear_generated_layers():
    rt.resetMaxFile(rt.name('noPrompt'))


def make_letter_object(char: str, name: str, extrude: float) -> object:
    """
    Create a single Text spline / ExtrudedText object for one character.

    Returns the 3ds Max object node.
    """
    if extrude > 0:
        # SplineShape with Extrude modifier — gives actual geometry depth
        txt = rt.text(
            text=char,
            size=FONT_SIZE,
            name=name,
            font=FONT,
        )
        # Centre the pivot (Max text is left-baseline by default)
        rt.resetXForm(txt)
        rt.collapseStack(txt)

        ext = rt.Extrude()
        ext.amount = extrude
        rt.addModifier(txt, ext)
    else:
        # Flat spline only
        txt = rt.text(
            text=char,
            size=FONT_SIZE,
            name=name,
            font=FONT,
        )
        rt.resetXForm(txt)

    return txt


def explode_words(word_arrays=None):
    clear_generated_layers()

    """
    Main entry point.  Mirrors explode_words() from the Blender version.

    Parameters
    ----------
    word_arrays : list[list[str]], optional
        If omitted, uses the module-level WORD_ARRAYS constant.
    """
    if word_arrays is None:
        word_arrays = WORD_ARRAYS

    for layer_idx, words in enumerate(word_arrays):
        layer_tag   = f"WordLayer_{layer_idx + 1}"
        layer_nodes = []   # collect nodes for the named selection set

        for row_idx, word in enumerate(words):
            for char_idx, char in enumerate(word):
                obj_name = f"{layer_tag}_r{row_idx}_c{char_idx}_{char}"

                node = make_letter_object(char, obj_name, EXTRUDE_DEPTH)

                # ── Position ──────────────────────────────────────────
                x = (char_idx + 0.5) * COLUMN_SPACING
                y = -(row_idx + 0.5) * ROW_SPACING
                z = (layer_idx + 0.5) * LAYER_SPACING

                node.pos = rt.Point3(x, y, z)

                # ── Rotation ──────────────────────────────────────────
                # See https://forums.autodesk.com/t5/3ds-max-programming-forum/how-to-rotate-a-box-around-its-local-axis-with-python/m-p/10922163
                node.transform *= pymxs.runtime.xformMat(pymxs.runtime.rotateZMatrix(LETTER_ANGLE_Z), pymxs.runtime.inverse(node.transform))
                node.transform *= pymxs.runtime.xformMat(pymxs.runtime.rotateYMatrix(LETTER_ANGLE_Y), pymxs.runtime.inverse(node.transform))
                node.transform *= pymxs.runtime.xformMat(pymxs.runtime.rotateXMatrix(LETTER_ANGLE_X), pymxs.runtime.inverse(node.transform))
                
                node.wirecolor = rt.color(255, 255, 255)

                layer_nodes.append(node)

        # Create / update a named selection set for this layer
        # (equivalent to Blender collection for organisational purposes)
        node_array = rt.Array(*layer_nodes) if layer_nodes else rt.Array()
        rt.selectionSets[layer_tag] = node_array

        print(f"[WordExploder] Created layer '{layer_tag}' "
              f"with {len(words)} word(s): {words}")

    print("[WordExploder] Done.")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    explode_words(WORD_ARRAYS)
