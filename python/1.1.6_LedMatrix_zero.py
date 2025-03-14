# DIN - MOSI(MO)
# CS - (CS)
# CLK - (SCK)

from fusion_hat import LedMatrix

rgb_matrix = LedMatrix(rotate=0)

#Define a simple pattern (e.g., a smiley face)

# pattern = [
#     0b00111100,
#     0b01000010,
#     0b10100101,
#     0b10000001,
#     0b10100101,
#     0b10011001,
#     0b01000010,
#     0b00111100
# ]

pattern = [
    0b01111110,
    0b01000000,
    0b00111100,
    0b00000010,
    0b00000001,
    0b00000001,
    0b01000010,
    0b00111100
]

rgb_matrix.display_pattern(pattern) 

# To keep the display on, prevent the script from exiting (e.g., with a loop)
input("Press Enter to exit...")
