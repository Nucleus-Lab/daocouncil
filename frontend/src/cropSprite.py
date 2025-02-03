from PIL import Image

# Open the sprite sheet
sprite_sheet = Image.open('./src/assets/Farm RPG FREE 16x16 - Tiny Asset Pack/Character/Idle.png')

# Crop the first 32x32 tile
first_tile = sprite_sheet.crop((0, 0, 32, 32))

# Save the cropped image
first_tile.save('./src/assets/character.png')

print("Sprite cropped successfully!") 