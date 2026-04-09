# Question Images Directory

This directory stores images for questions. Images are optional and can be added to any question.

## How to Add Images to Questions

### Step 1: Add the Image File
1. Place your image file in this `questions/images/` directory
2. Supported formats: PNG, JPG, JPEG, GIF, BMP
3. Recommended size: 400x300 pixels or smaller (will be automatically scaled)

### Step 2: Reference the Image in Question File
Add an `Image:` line to your question in the question file:

```
What is shown in this diagram?
a. Water Cycle
b. Carbon Cycle
c. Nitrogen Cycle
d. Oxygen Cycle
Image: water_cycle_diagram.png
Explanation: This diagram shows the water cycle process.
```

### Example Question with Image

```
What process is shown in this image?
a. Photosynthesis
b. Respiration
c. Transpiration
d. Germination
Image: photosynthesis_diagram.png
Explanation: The image shows a plant using sunlight, water, and carbon dioxide to make food.
```

## Image Naming Tips

- Use descriptive names: `water_cycle.png`, `solar_system.png`
- Use lowercase and underscores: `states_of_matter.png`
- Keep file names short but clear
- Use PNG format for diagrams with transparency
- Use JPG for photos

## Image Guidelines

- **Size**: Images will be automatically scaled to fit (max 400x200 pixels in question view)
- **Content**: Use clear, educational images that help students understand the concept
- **Quality**: Use high-quality images that are clear when scaled down
- **Copyright**: Only use images you have permission to use (free educational resources, your own images, etc.)

## File Structure

```
questions/
├── water_cycle.txt
├── states_of_matter.txt
├── ...
└── images/
    ├── water_cycle_diagram.png
    ├── photosynthesis_diagram.png
    └── solar_system_map.jpg
```

## Notes

- Images are optional - questions work fine without them
- If an image file is not found, the question will display normally without the image
- Images are cached in memory for better performance
- The `Image:` line can be placed anywhere after the options (a, b, c, d)
