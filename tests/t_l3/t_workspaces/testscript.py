import os
import sys

print(sys.path)
print(os.getcwd())

import PIL.Image as Image
from engine.l3_aos.aos import AOS
_, __ = Image, AOS(workspaces=[])

print('Hello world!')
raise Exception(f'fuck you')

a

# 2+2 = 4