from PIL import Image
import os

def crop_sprite_sheet(input_path, output_dir):
    # Get character filename (e.g., 'F_01' or 'M_01')
    char_name = os.path.splitext(os.path.basename(input_path))[0]
    
    # Create character directory in the output folder
    char_dir = os.path.join(output_dir, char_name)
    if not os.path.exists(char_dir):
        os.makedirs(char_dir)
        print(f"Created directory: {char_dir}")

    # Open the sprite sheet
    try:
        sprite_sheet = Image.open(input_path)
        print(f"Processing: {input_path}")
    except Exception as e:
        print(f"Error loading sprite sheet {input_path}: {e}")
        return

    # Define sprite dimensions
    sprite_width = 16
    sprite_height = 17
    rows = 3
    cols = 4

    # Define naming conventions
    directions = ['front', 'right', 'back', 'left']
    actions = ['idle', 'walk_1', 'walk_2']

    # Crop and save individual sprites
    for row in range(rows):
        for col in range(cols):
            # Calculate crop coordinates
            left = col * sprite_width
            top = row * sprite_height
            right = left + sprite_width
            bottom = top + sprite_height

            # Crop the sprite
            sprite = sprite_sheet.crop((left, top, right, bottom))

            # Generate output filename: direction_action.png
            filename = f"{directions[col]}_{actions[row]}.png"
            output_path = os.path.join(char_dir, filename)

            # Save the sprite
            sprite.save(output_path)
            print(f"Saved {char_name}/{filename}")

def process_all_characters():
    # Base directory is now the current directory
    base_dir = "."
    
    # Create output directory
    output_dir = os.path.join(base_dir, "cropped")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # Process both Males and Females folders
    for gender in ['Males', 'Females']:
        gender_dir = os.path.join(base_dir, gender)
        
        # Skip if directory doesn't exist
        if not os.path.exists(gender_dir):
            print(f"Directory not found: {gender_dir}")
            continue

        # Process each character file in the gender directory
        for filename in os.listdir(gender_dir):
            if filename.endswith('.png'):
                input_path = os.path.join(gender_dir, filename)
                crop_sprite_sheet(input_path, output_dir)

    print("All character sprites processed!")

if __name__ == "__main__":
    process_all_characters() 