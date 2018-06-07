import fastzbarlight
import numpy as np
import zbarlight

img = np.load('trial.npy')

import timeit
num = 1000
duration = timeit.timeit(lambda: zbarlight.qr_code_scanner(img.tobytes(), 100, 100), number=num)
print('Average call time with zbarlight: %sms (%d tries)' % (duration/num*1000, num))

duration = timeit.timeit(lambda: fastzbarlight.qr_code_scanner(img.tobytes(), 100, 100), number=num)
print('Average call time with fastzbarlight: %sms (%d tries)' % (duration/num*1000, num))

# from PIL import Image
# img = Image.fromarray(img.reshape((100, 100)))

# img.save('trial.png')
# duration = timeit.timeit(lambda: zbarlight.scan_codes('qrcode', img), number=num)
# print('Average call time with image 2.0: %sms' % (duration/num*1000))
