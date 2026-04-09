# Questions Directory

This directory contains text files with science questions for the game.

## File Format

Each question file should follow this format:

```
Question text here?
a. First option (this is always the correct answer)
b. Second option
c. Third option
d. Fourth option
Image: optional_image.png
Explanation: Optional explanation text that helps students understand the answer

Next question text?
a. Correct answer
b. Wrong answer
c. Wrong answer
d. Wrong answer
Explanation: Optional explanation

(Blank line between questions)
```

## Important Rules

1. **Option 'a' is always the correct answer** - The game will automatically use option 'a' as the correct answer
2. **Four options required** - Each question must have exactly four options (a, b, c, d)
3. **Blank lines separate questions** - Use blank lines to separate different questions
4. **Images are optional** - Add `Image: filename.png` after the options to include a picture (place images in `questions/images/` folder)
5. **Explanations are optional** - You can include an explanation after the options, or omit it
6. **File naming** - Files should be named: `topic_name.txt` (e.g., `water_cycle.txt`)

## Example

```
What is the process called when water turns into water vapor?
a. Evaporation
b. Condensation
c. Precipitation
d. Collection
Explanation: Evaporation is when liquid water turns into water vapor (gas).

What process is shown in this diagram?
a. Water Cycle
b. Carbon Cycle
c. Nitrogen Cycle
d. Oxygen Cycle
Image: water_cycle_diagram.png
Explanation: This diagram shows the complete water cycle process.

What happens during condensation in the water cycle?
a. Water vapor turns into liquid
b. Liquid turns into ice
c. Ice turns into water
d. Water flows downhill
Explanation: Condensation is when water vapor cools down and turns back into liquid water, forming clouds.
```

## Adding Images to Questions

1. Place your image file in the `questions/images/` directory
2. Add `Image: filename.png` line after the options (a, b, c, d)
3. Supported formats: PNG, JPG, JPEG, GIF, BMP
4. Images are automatically scaled to fit the screen
5. See `images/README.md` for more details

## Adding New Questions

1. Open the appropriate topic file (e.g., `water_cycle.txt`)
2. Add your question following the format above
3. Make sure option 'a' is the correct answer
4. Save the file
5. Restart the game to load new questions

## Adding New Topics

1. Create a new `.txt` file in this directory (e.g., `chemistry.txt`)
2. Add questions following the format
3. Update `questions.py` to include the new topic in the `topic_files` dictionary:
   ```python
   topic_files = {
       ...
       "chemistry": "chemistry.txt"
   }
   ```
4. Update `main.py` to include the new topic in the `topics` list

## Current Topics

- `water_cycle.txt` - Water Cycle questions
- `states_of_matter.txt` - States of Matter questions
- `solar_system.txt` - Solar System questions
- `plants.txt` - Plant biology questions
- `animals.txt` - Animal biology questions
