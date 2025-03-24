import os
import sys

print(sys.path)
print(os.getcwd())

import PIL.Image as Image
from engine.l3_aos.aos import AOS

aos = AOS(workspaces=[])

_ = Image


print('Hello world!')

raise Exception(f'fuck you')

