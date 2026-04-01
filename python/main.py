import time

from defcon import Font
from ufo2ft import compileOTF

print("hello, world")

# time
start = time.time()

ufo = Font("main.ufo")
otf = compileOTF(ufo)
otf.save("out.otf")
end = time.time()
print(f"Time taken: {(end - start) * 1000}ms")