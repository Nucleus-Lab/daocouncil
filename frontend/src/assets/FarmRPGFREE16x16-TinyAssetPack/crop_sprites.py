from PIL import Image
import os

def crop_sprite_sheet(input_path, output_dir):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

        print(f"Created directory: {output_dir}")

    # Open the sprite sheet
    try:
        sprite_sheet = Image.open(input_path)
        print(f"Loaded sprite sheet: {input_path}")
    except Exception as e:
        print(f"Error loading sprite sheet: {e}")
        return

    # Define sprite dimensions
    sprite_width = 32
    sprite_height = 32
    rows = 3
    cols = 4


    # Define row names
    row_names = ['idle_front', 'idle_back', 'idle_right']


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

            # Generate output filename
            filename = f"{row_names[row]}_{col}.png"
            output_path = os.path.join(output_dir, filename)

            # Save the sprite
            sprite.save(output_path)
            print(f"Saved sprite: {filename}")

    print("Sprite sheet processing complete!")

if __name__ == "__main__":
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set up paths relative to the script location
    input_path = r"Character\Idle.png"
    output_dir = os.path.join(script_dir, 'idle_sprites')

    crop_sprite_sheet(input_path, output_dir) 