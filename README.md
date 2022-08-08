# Kiro

This is a Blender addon that helps quickly cloning keyboard keys, typewriters, letter-game tiles,
and other such items that can be textured by an image grid of letters and symbols. It's called "Kiro" because it
makes keys in rows. Get it?

## The (sad, sad) state of things

This is very much a work in progress at the current time. Expect more documentation and functionality
in the future. Expect things to be a bit slapdash and crude in the current code.

## To install

Rename the `src` directory and put it into your Blender addons directory. I'll get releases together with
proper ZIP files sometime here.

## To use

### General Principles

Kiro allows you to use a "sprite sheet" image texture of letters or keycap images, in one or more grids, to
create a keycap object (or other such thing-with-a-letter-on-it), then quickly clone that to more objects with
different letters. It accomplishes this by coordinating a few different parts:

1. **The Texture** - An image with a grid of letters, keycaps, etc.
2. **The "Grid Picker" Nodegroup** - This takes a single UV and some positioning information, and repositions
   the UV over a selected grid cell.
3. **The `keycap` Attribute** - Attach an Attribute node with the `keycap` attribute, and you can drive which
   keycap gets shown based on an Object Custom Property
4. **Metadata** - Add a JSON file alongside the texture image, and you can associate grid cells with letters or
   names, allowing you to simply type in strings of keycaps or (future feature) generate whole keyboard layouts
   given only one representative key. 
5. **The Kiro Addon** - The Kiro addon has operators that allow you to create strings of keycaps just by
   typing or specifying a string length.

### Using a pre-made keycap set

1. Model a single keycap
2. Apply the keycap texture where appropriate
3. Apply the UVs on the keycap to the upper-left grid cell of the image
4. Add and configure "Grid Picker" nodes and connect the Attribute node to the Grid Picker Index input
5. Add the "keycap" Custom Property in the Object Properties panel
6. Linked-duplicate (Alt+D) this where needed
7. Select the keycap and bring up the context menu (Spacebar or W, depending on configuration)
8. Run the Kiro tools to type out or build strings of duplicates. All duplicates are linked duplicates, which
   minimizes memory usage when rendering.

This should get easier in the future as I add tools to generate the nodes and properties in steps 4 and 5

### Making your own keycap set

1. Make an image texture with a grid of keycaps. (TODO insert details)
2. Make a JSON file detailing which keys are in which cells.

## To-dos

### Upcoming Features

* Support packing JSON into Text nodes and using packed images (If possible, hook the packing feature. If not, make an action.)
* Support grouping or parenting to a new object

## Long-future Features

* Multiline text support
* Keycap libraries and cloning multiple objects
* UV baking (apply Attributes and Grid Picker to simple UVs)
