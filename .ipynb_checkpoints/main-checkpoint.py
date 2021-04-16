from PIL import ImageFont
from Text_Objects import *
from doc import Document
import utils
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from glob import glob
import os
import random
import uuid
import textwrap
import re

#main에 필요한 값들 먼저 정리 후, yaml format 정리

# 하나의 corpus에 대해 정의해야할 부분
# font






def save(txt_dir, save_dir, page_dir, bbox_level = ['char']) :
    
    pagesize = (595, 842)
    
    template = []
    
    
    # 완전 랜덤 coordinate assignment
#     x, y = random.uniform(0, pagesize[0]/6), random.uniform(0, pagesize[1]/6)
    
#     for i in range(n) :
#         font_prop = {'dir' : random.choice(glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'font/*'))) ,
#                  'size' : random.randint(10, 15)}
        
#         print(font_prop)
#         txt_file = random.choice(glob(os.path.join(txt_dir, '*.txt')))
        

#         random_angle = random.randint(-3,3)

#         page_info = {
#             'size' : (595, 842),
#             'color' : 'white',
#             'angle' : random_angle
#         }

        
#         # corpus 작성
#         corpus = build_corpus(txt_file, xy = (x, y), font_prop = font_prop)
        
#         # template 구성 padding_h만 더함 지금까지는(~01/27)
#         template.append(corpus)
        
#         x += random.uniform(0, 40)
#         y += corpus.height + random.uniform(0, 50)


    # block divided random assignment
    n = 1 #random.randint(3,6)
    block_dic = utils.block(pagesize, n)
    block_coords = utils.assign_block(block_dic)
    
    random_angle = 0 #random.randint(-2,2)
    
    page_info = {
            'size' : (595, 842),
            'color' : 'white',
            'angle' : random_angle,
            'page' : random.choices([page_dir, None], weights = [0.7, 0.3])[0]
        }
    txt_file = random.choice(glob(os.path.join(txt_dir, '*.txt')))
    
    with open(txt_file) as f :
        data = ' '.join(f.read().split('\n'))
    
    # filtering
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'str_dict.txt'), 'r', encoding='utf8') as f:
        str_dic = f.read()
        # wiki 데이터에 html/markdown 문법 제거용
    str_dic = re.sub(r'\[\[(?:[^\]|]*\|)?([^\]|]*)\]\]\{\}\[', '', str_dic)
    
    data = ''.join(list(filter(lambda char: char in str_dic, data)))
    
    texts = textwrap.wrap(data,len(data)//n)
    
    for text, block_coord in zip(texts, block_coords) :
        font_prop = {'dir' : random.choice(glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'font/*'))) ,
                 'size' : random.randint(13, 19)}

        #xy
        #x, y = block_coord[0], block_coord[1] 04/01
        x, y = random.randint(10, 100), random.randint(30, 300)
        
        #padding_h
        padding_h = random.randint(10, 30)
        # corpus_w 
        w, h = page_info['size']
        corpus_w = random.randint(w - 80, w )#block_coord[2] - block_coord[0] 04/01
        
        corpus_h = random.randint(h - 80, h )#block_coord[-1] - block_coord[1] 04/01
        #padding_w
        padding_w = 10#0
        
        corpus = build_corpus(text, 
                              xy = (x,y), 
                              font_prop = font_prop, 
                              padding_h = padding_h, 
                              corpus_w = corpus_w,
                              corpus_h = corpus_h,
                              padding_w = padding_w )

        template.append(corpus)
    
    
    # background effect 추가
    g = Document(page_info, template)
    
    g.assign()
    
    
    g.rotate(page_info['angle'])
    g.page =  g.background_effect(g.page)
    
    
    # object to save
    img_arr = g.get_page()

    ####
    bbox_objs = {}
    for blevel in bbox_level :
        bbox_objs[blevel] = g.get_bbox(blevel)
    ####
#         bbox_objs[g.get_bbox(bbox_level))
    
    
    
    # save names
    gt_file = os.path.join(save_dir,'gt', 'augdoc'+str(page_info['angle'])+'_'+uuid.uuid4().hex[:15]+'.txt')
    
    img_file = gt_file.replace('.txt', '.jpg').replace('gt', 'img')    
    
    os.makedirs(os.path.dirname(img_file), exist_ok = True)
    os.makedirs(os.path.dirname(gt_file),  exist_ok = True)
    
#     return img_arr

    plt.imsave(img_file, img_arr )
    
    # save bbox info
    
    if random_angle : 
        for blevel, bbox_obj in bbox_objs.items() :
            txt_ls = []
            with open(os.path.splitext(gt_file)[0]+'_'+blevel+'.txt', 'w', encoding='utf8') as f :
                for txt, bbox in bbox_obj :
                    bbox_ls = []
                    bbox_ls.append(txt)
                    coord_ls = bbox.flatten().tolist()
                    for c in coord_ls :
                        bbox_ls.append(str(c))
                    v = '\t'.join(bbox_ls)
                    txt_ls.append(v)
                f.write('\n'.join(txt_ls))
                
#             f.write('\n'.join([txt+'\t'+str(bbox) for txt, bbox in bbox_objs]))

    else :
        for blevel, bbox_obj in bbox_objs.items() :
            txt_ls = []
            with open(os.path.splitext(gt_file)[0]+'_'+blevel+'.txt', 'w', encoding='utf8') as f :
                for obj in bbox_obj :
                    bbox_ls = []
                    bbox_ls.append(obj.text)
                    coord_ls = '\t'.join([str(_) for _ in obj.bbox])
                    bbox_ls.append(coord_ls)
                    v = '\t'.join(bbox_ls)
                    txt_ls.append(v)
                f.write('\n'.join(txt_ls))
            
#             f.write('\n'.join([obj.text+'\t'+str(obj.bbox) for obj in bbox_objs]))
    return g
    

def build_corpus(txt, xy, font_prop, padding_h, padding_w, corpus_h,corpus_w) :
    
    #font
    font = ImageFont.truetype(font_prop['dir'], \
                              font_prop['size'])

    align = random.choice(['left'])
    
    return Corpus(corpus = txt,
                  font = font,
                  xy = xy,
                  padding_h = padding_h,
                  padding_w = padding_w,
                  corpus_w = corpus_w,
                  corpus_h = corpus_h,
                  align = align)




if __name__ == "__main__":
    save(txt_dir = '/home/jovyan/work/3_project_data/TwinReader/augdata/textdata4full_lines/navernews',
         save_dir = '/home/jovyan/work/3_project_data/TwinReader/augdata/sample0127',
         n = 2
        )