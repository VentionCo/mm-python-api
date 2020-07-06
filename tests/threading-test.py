import threading
import time

def f1() :
    time.sleep(10.0)
    return

t1 = threading.Thread(target = f1)

t1.start()

t1.join(6.0)

print(t1.isAlive())
