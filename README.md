# Kiro

This is a Blender addon that helps quickly cloning keyboard keys, typewriters, letter-game tiles,
and other such items that can be textured by an image grid of letters and symbols. It's called "Kiro" because it
makes keys in rows. Get it?

## The (sad, sad) state of things

This is very much a work in progress at the current time. Expect more documentation and functionality
in the future. Expect things to be a bit slapdash and crude until then.

## To install

Rename the `src` directory and put it into your Blender addons directory, or ZIP it up and install it.
I'll get releases together with proper ZIP files sometime here.

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
2. Load the Image for the keycap texture (It'll blow up on you if you don't load the image first-- known bug, will fix)
3. Apply relevant UVs on the keycap to the upper-left grid cell of the image
4. In the Shader Editor, Add "Kiro: Add Shader Nodes". Check the "Add Custom Property (keycap)" checkbox.
5. Attach the output of the resulting Image Texture node to where it ought to go.
6. Back in Layout, select the keycap and bring up the context menu (Spacebar or W, depending on your Blender
   configuration). Use one of the "Kiro" menu items to clone the keycap you made. Be sure to select the right
   Keyset (the list at the bottom), because only the keys that exist in the Keyset will be created.

### Making your own keycap set

***This needs a more thorough howto, as it's a bit complicated and precise. It's coming soon.***

1. Make an image texture with a grid of keycaps.
2. Make a JSON file detailing which keys are in which cells.

## To-dos

### Next-up Fixes

* Allow loading an image that isn't already in the file.
* Document the JSON file format and how to make your own keycap sets
* Have a verifier for the JSON file so it doesn't just unceremoniously choke on bad JSON 

### Upcoming Features

* Support packing JSON into Text nodes and using packed images (If possible, hook the packing feature. 
  If not, make an action.)
* Support grouping and/or parenting to a new object

### Long-future Features

* Multiline text support
* Keycap libraries and cloning multiple objects
* UV baking (apply Attributes and Grid Picker to simple UVs)
