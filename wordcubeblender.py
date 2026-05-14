import bpy
import bmesh
from mathutils import Vector
from math import radians

WORD_ARRAYS = [
    ["OSTLER", "SERENE", "TRYSTS", "LESSEE", "ENTERA", "RESEAL"],
    ["TERETE", "EMETIN", "RELENT", "ETERNE", "TINNER", "ENTERA"],
    ["SHOVEL", "HALITE", "OLIVES", "VIVERS", "ETERNE", "LESSEE"],
    ["ESCORT", "STALER", "CAGILY", "OLIVES", "RELENT", "TRYSTS"],
    ["RUSHES", "UNTAME", "STALER", "HALITE", "EMETIN", "SERENE"],
    ["PRESTO", "RUSHES", "ESCORT", "SHOVEL", "TERETE", "OSTLER"],
]

# Visual settings
FONT_SIZE       = 0.25  # base font size before scaling
EXTRUDE_DEPTH   = 0.01  # how much to extrude text into 3-D (0 = flat)
BEVEL_DEPTH     = 0  # bevel on text edges (0 = none)
LETTER_ANGLE_X  = 45    # letter angle along x axis in degrees    
LETTER_ANGLE_Y  = 0     # letter angle along y axis in degrees
LETTER_ANGLE_Z  = -45   # letter angle along z axis in degrees
# TODO implement Matplotlib's font_manager to set fonts
# See: https://stackoverflow.com/a/75069120
# Maybe Verdana, Franklin Gothic (NYT games font), or Comic Sans. Probably bolded.

def clear_generated_collections():
    """Remove previously generated 'WordLayer_*' collections and their objects."""
    for col in list(bpy.data.collections):
        if col.name.startswith("WordLayer_"):
            for obj in list(col.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(col)

def make_letter_object(char: str, name: str) -> bpy.types.Object:
    """Create a single text object for one character."""
    curve = bpy.data.curves.new(name=name, type='FONT')
    curve.body          = char
    curve.size          = FONT_SIZE
    curve.extrude       = EXTRUDE_DEPTH
    curve.bevel_depth   = BEVEL_DEPTH
    curve.align_x       = 'CENTER'
    curve.align_y       = 'CENTER'
    obj = bpy.data.objects.new(name=name, object_data=curve)
    return obj

def explode_words(word_arrays=None):
    """
    Main entry point.

    Parameters
    ----------
    word_arrays : list[list[str]], optional
        If omitted, uses the module-level WORD_ARRAYS constant.
    """
    if word_arrays is None:
        word_arrays = WORD_ARRAYS

    clear_generated_collections()

    scene = bpy.context.scene

    for layer_idx, words in enumerate(word_arrays):
        # ── Create collection ────────────────────────────────────────────
        col_name = f"WordLayer_{layer_idx + 1}"
        collection = bpy.data.collections.new(col_name)
        scene.collection.children.link(collection)

        # Gather all letter objects first (unscaled) to measure layout
        # Structure: rows[word_idx] = list of (obj, char) tuples
        rows = []
        for word in words:
            letters = []
            for char in word:
                name = f"L{layer_idx}_{len(rows)}_{char}_{len(letters)}"
                obj  = make_letter_object(char, name)
                collection.objects.link(obj)
                scene.collection.objects.link(obj)  # temp link for ops
                letters.append(obj)
            rows.append(letters)

        # ── Position letters ──────────────────────────────────────────
        # Y: stack rows top-to-bottom, centered at Y=0
        for row_idx, letters in enumerate(rows):
            for char_idx, obj in enumerate(letters):
                obj.location = (char_idx, -row_idx, 0.0)
                obj.rotation_euler = (radians(LETTER_ANGLE_X), radians(LETTER_ANGLE_Y), radians(LETTER_ANGLE_Z))

        # ── Offset each layer along Z so layers don't overlap ─────────
        z_offset = layer_idx
        for letters in rows:
            for obj in letters:
                obj.location.z += z_offset
                obj.location.z += 0.5
                obj.location.y += -0.5
                obj.location.x += 0.5

        # Clean up temporary scene-level links (keep only collection link)
        for letters in rows:
            for obj in letters:
                if obj.name in scene.collection.objects:
                    scene.collection.objects.unlink(obj)

        print(f"[WordExploder] Created layer '{col_name}' "
              f"with {len(words)} word(s): {words}")

    print("[WordExploder] Done.")


# Run when executed directly inside Blender
if __name__ == "__main__":
    explode_words(WORD_ARRAYS)
