import numpy as np
import scipy.ndimage as ndi
from random import randint
from numpy import *
import pylab
import random
import skimage

def fulltxt2list(fulltext, delimiter) :
    return fulltext.split(delimiter)

def text2lines(text,width) :
    line_ls = []
    line = ''
    for t in text :
        line += t
        w = font.getbbox(line)[2] - font.getbbox(line)[0]
        if w >= width :
            line_ls.append(line)
            line = ''
    if line != '' :
        line_ls.append(line)
    return line_ls


def get_table(xy, table_info, fulltext, num_row, num_col, delimiter = ',', line = False) : 
    (x,y) = xy
    table_w, table_h = table_info
    # table_h는 text의 길이에 따라 설정
    cell_w = table_w/num_col
    cell_h = table_h/num_row
    
    txt_ls = fulltxt2list(fulltext, delimiter)
    cp_ls = []
    
    for i, txt in enumerate(txt_ls) :
        r_num = i//num_col
        c_num = (i - r_num*num_col) % num_col
        
        cell_x = x + (cell_w*c_num)
        cell_y = y + (cell_h*r_num)
        
        txt_w, txt_h = font.getsize(txt)
        cp = Corpus(corpus = txt,
                    xy = (cell_x + (cell_w - txt_w)/2, cell_y + (cell_h - txt_h)/2),
                    font = font ,
                    corpus_w = cell_w,
                    padding_h = 3) # align on the middle
        cp_ls.append(cp)

    return cp_ls

def get_table_lines(xy, table_info, num_row, num_col) :
    (x,y) = xy
    table_w, table_h = table_info
    cell_w = table_w/num_col
    cell_h = table_h/num_row
    
    line_ls = []
    for r in range(num_row+1) :
        line_ls.append([(x, y+r*cell_h), (x+table_w, y+r*cell_h)])
    for c in range(num_col+1) :
        line_ls.append([(x+c*cell_w, y), (x+c*cell_w, y+table_h)])

    return line_ls

def random_blobs(shape, blobdensity, size, roughness=2.0):
    from random import randint
    from builtins import range  # python2 compatible
    h, w = shape
    numblobs = int(blobdensity * w * h)
    mask = np.zeros((h, w), 'i')
    for i in range(numblobs):
        mask[randint(0, h-1), randint(0, w-1)] = 1
    dt = ndi.distance_transform_edt(1-mask)
    mask =  np.array(dt < size, 'f')
    mask = ndi.gaussian_filter(mask, size/(2*roughness))
    mask -= np.amin(mask)
    mask /= np.amax(mask)
    noise = pylab.rand(h, w)
    noise = ndi.gaussian_filter(noise, size/(2*roughness))
    noise -= np.amin(noise)
    noise /= np.amax(noise)
    return np.array(mask * noise > 0.5, 'f')

def random_blotches(image, fgblobs, bgblobs, fgscale=10, bgscale=10):
    fg = random_blobs(image.shape, fgblobs, fgscale)
    bg = random_blobs(image.shape, bgblobs, bgscale)
    return minimum(maximum(image, fg), 1-bg)

def percent_black(image):
    n = prod(image.shape)
    k = sum(image < 0.5)
    return k * 100.0 / n

def binary_blur(image, sigma = 0.001, noise=0.0):
    p = percent_black(image)
    print(image)
    blurred = ndi.gaussian_filter(image, sigma)
    if noise > 0:
        blurred += np.array(pylab.randn(*blurred.shape) * noise, dtype = np.uint8)
    t = np.percentile(blurred, p)
    return np.array(blurred > t, 'f')

def block(pagesize, n) :
    w,h = pagesize
    n_w = random.randint(1,4)
    n_h = n //  n_w
    if n_h == 0 :
        n_h += 1
    
    block_w = w/n_w
    block_h = h/n_h
    
    
    block_dic = {}
    i = 0 
    for col in range(n_h) :
        for row in range(n_w) :
            
            block_dic[i] = (row*block_w+20, col*block_h, (row+1)*block_w, (col+1)*block_h )
            i += 1
    return block_dic

def assign_block(block_dic) :

    N = len(block_dic)

    n_samp = random.randint(1, N)
    assigned_blocks = random.sample(list(block_dic.keys()), n_samp)
    block_coords = [block_dic[block] for block in assigned_blocks]
    
    return block_coords


def inrange(size, coord) :
    x0,y0,x1,y1 = coord
    if 0 <= x0 and size[0] >= x0 \
    and 0 <= x1 and size[0] >= x1 \
    and 0 <= y0 and size[1] >= y0 \
    and 0 <= y1 and size[1] >= y1 :
        return True
    else :
        return False
