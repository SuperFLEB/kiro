# Kiro

This is a Blender addon that helps quickly cloning keyboard keys, typewriters, letter-game tiles, and other such items
that can be textured by an image grid of letters and symbols. It's called "Kiro" because it makes keys in rows. Get it?

## The state of things

This is a work in progress at the moment. The addon functions, but expect more documentation and more polish in the
future.

## To install

Rename the `src` directory and put it into your Blender addons directory, or ZIP it up and install it. I'll get releases
together with proper ZIP files sometime here.

### jsonschema Python requirement

Though it is not required for basic functionality, this addon uses the `jsonschema` Python package is used to validate
*.kiro.json sidecar files. It can be one-click installed (and uninstalled) with the button in the addon's Preferences
panel. If it is not installed, the addon will function as expected, except for the fact that having an image with a
broken JSON sidecar file may cause instability in the addon, and the Kiro Report feature will not validate JSON files.

## To use

### General Principles

Kiro allows you to use a "sprite sheet" image texture of letters or keycap images, in one or more grids, to create a
keycap object (or other such thing-with-a-letter-on-it), then quickly clone that to more objects with different letters.
It accomplishes this by coordinating a few different parts:

1. **The Texture** - An image with a grid of letters, keycaps, etc.
2. **The "Grid Picker" Nodegroup** - This takes a single UV and some positioning information, and repositions the UV
   over a selected grid cell.
3. **The `keycap` Attribute** - Attach an Attribute node with the `keycap` attribute, and you can drive which keycap
   gets shown based on an Object Custom Property
4. **Metadata** - Add a JSON file alongside the texture image, and you can associate grid cells with letters or names,
   allowing you to simply type in strings of keycaps or (future feature) generate whole keyboard layouts given only one
   representative key.
5. **The Kiro Addon** - The Kiro addon has operators that allow you to create strings of keycaps just by typing or
   specifying a string length.

See the `demo` directory in this repo for an example of how to set up the pieces.

### Using a pre-made keycap set

1. Model a single keycap
2. Load the Image for the keycap texture (It'll blow up on you if you don't load the image first-- known bug, will fix)
3. Apply relevant UVs on the keycap to the upper-left grid cell of the image
4. In the Shader Editor, Add "Kiro: Add Shader Nodes". Check the "Add Custom Property (keycap)" checkbox.
5. Attach the output of the resulting Image Texture node to where it ought to go.
6. Back in Layout, select the keycap and bring up the context menu (Spacebar or W, depending on your Blender
   configuration). Use one of the "Kiro" menu items to clone the keycap you made. Be sure to select the right Keyset (
   the list at the bottom), because only the keys that exist in the Keyset will be created.

### Making your own keycap set

***This needs a more thorough howto, as it's a bit complicated and precise. It's coming soon.***

1. Make an image texture with a grid of keycaps.
2. Make a JSON file detailing which keys are in which cells. Call it (imagename).kiro.json and put it in the same place
   as the image. (e.g., if your image is "something.png", make "something.kiro.json")
3. Fill out the JSON file similar to the demo. This is the part that really needs more documentation.

#### Validating

***This needs a more thorough howto, as well.***

Your .kiro.json files can be checked for validity inside Blender. To check them:

1. Be sure the `jsonschema` Python package is installed. Use the button in the Preferences panel for the addon to
   install it.
2. Make a new Blender document and load the image. It doesn't have to be applied to anything, just loaded, so loading it
   from the UV or Image editor will work.
3. In the Edit menu, under the Kiro submenu, select "Generate Kiro Image Report".
4. The report will be written to a Text block in the current Blender document. To see it, go to the Scripting workspace
   and open it using the dropdown.

If everything checks out, congratulations! You have a semantically valid Kiro file.

## To-dos

### Next-up Fixes

* Add an option to put the generated keys into a new collection
* Put more logical validity checks in the report generator. Check for "alt_for" relationships, bounds on numbers, etc.
* Document the JSON file format and how to make your own keycap sets
* Allow loading an image that isn't already in the file from the Kiro interface.

### Upcoming Features

* Support packing JSON into Text nodes and using packed images (If possible, hook the packing feature. If not, make an
  action.)
* Support grouping and/or parenting to a new object

### Long-future Features

* Multiline text support
* Keycap libraries and cloning multiple objects
* UV baking (apply Attributes and Grid Picker to simple UVs)
