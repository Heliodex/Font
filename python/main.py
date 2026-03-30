from defcon import Font
from ufo2ft import compileOTF

print("hello, world")

ufo = Font("main.ufo")
otf = compileOTF(ufo)
otf.save("out.otf")
