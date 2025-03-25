import sys

print(f'Hello world :)')
print(print(f'sys.path: {sys.path}'))

import PIL.Image as Image
from engine.l3_aos.aos import AOS
_, __ = Image, AOS(workspaces=[])

print('Hello world!')
raise Exception(f'fuck you')

# 2+2 = 4