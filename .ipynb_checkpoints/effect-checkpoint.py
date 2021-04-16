import numpy as np 
import matplotlib.pyplot as plt
import cv2
import scipy.ndimage as ndi
from matplotlib.path import Path
import matplotlib.patches as patches
import random
import skimage
from PIL import Image, ImageFilter

# Take Image Object

def blur(img, fsize = (2,2)) :
    '''
    src img
    filter size
    '''
    return img.filter(ImageFilter.GaussianBlur(1))
    
def detail(img) :
    return img.filter((ImageFilter.DETAIL))
    
def random_blob(img) :
    '''
    not yet implemented
    https://stackoverflow.com/questions/50731785/create-random-shape-contour-using-matplotlib 참고
    '''
    # 원 기준에서 edge를 땡기고, perturb(섭동)해서 random한 shape 구성
    edges_n = random.randint(10) # 꼭짓점
    mag_pert = random.uniform(0,1)
    pts_n = edges_n*3+1 # number of points
    
    return img
    
def brightness(img) :
    '''
    not yet implemented
    '''
    img = np.array(img)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    value = random.randint(0,50)
    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value

    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2RGB)

    return Image.fromarray(img)

def binary_blur(image, sigma=0.1, noise=0.01):
    '''
    sigma = 0.0 ~ 3.0
    noise = 0.0 ~ 0.3
    sigma makes character noisy, noise makes document noisy
    '''
    def percent_black(image):
        n = np.prod(image.shape, dtype = np.uint8)
        k = sum(image < 0.5)
        return k * 100.0 / n
    image = np.array(image)
    p = percent_black(image)
    blurred = ndi.gaussian_filter(image, sigma)
    if noise > 0:
        blurred += np.random.randn(*blurred.shape, dtype = np.uint8) * noise
    t = np.percentile(blurred, p)
    return Image.fromarray(np.array(blurred > t, 'f'))

def gaussian_blur(image):
    image = np.array(image)
    blur_val = random.randint(0,1)
    print(blur_val)
    img = ndi.gaussian_filter(image, blur_val)
    return Image.fromarray(img)


def random_crop(image) :
    '''
    PIL image object
    '''
    w,h = image.size
    crop_w, crop_h = random.randint(20 ,w//2) , random.randint(20 , h//2)

    crop_xy = (150, 70)
    cropped_box = (crop_xy[0], crop_xy[1], crop_xy[0] + crop_w, crop_xy[1] + crop_h )
    cropped = image.crop(cropped_box)
    cropped_arr = np.array(cropped)
    cropped_arr = np.zeros_like(cropped_arr)
    cropped = Image.fromarray(cropped_arr)
    image.paste(cropped, cropped_box)
    
    return cropped_box

def motion_blur(img):
    img_arr = np.array(img)
    kernel_size = random.randint(3,5)
    kernel_v = np.zeros((kernel_size, kernel_size))
    kernel_h = np.copy(kernel_v)
    kernel_v[:, int((kernel_size - 1) / 2)] = np.ones(kernel_size)
    kernel_h[int((kernel_size - 1) / 2), :] = np.ones(kernel_size)
    # Normalize.
    kernel_v /= kernel_size
    kernel_h /= kernel_size
    # Apply the vertical kernel.
    blur_type = ['horizontal', 'vertical']
    blur_t = random.choice(blur_type)
#     print('blur type:',blur_t)
    if blur_t == 'vertical':
        vertical_mb = cv2.filter2D(img_arr, -1, kernel_v)
        return Image.fromarray(vertical_mb)
    else:
        horizonal_mb = cv2.filter2D(img_arr, -1, kernel_h)
        return Image.fromarray(horizonal_mb)
    
    
    

def noise(img) :
    img = np.array(img)
    noise_type = random.choice(['localvar','poisson','salt','pepper','s&p','speckle',])
    noised = (255*skimage.util.random_noise(img, noise_type)).astype(np.uint8)
    
    return Image.fromarray(noised)