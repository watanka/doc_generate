from PIL import Image, ImageDraw, ImageChops
import numpy as np
import matplotlib.pyplot as plt
import cv2
from Text_Objects import *
from utils import random_blotches, binary_blur
from effect import *
import utils
from glob import glob
import os, random
# import sys
# sys.path.append('./ocrodeg')
# from ocrodeg import binary_blur
# import ocrodeg
import scipy.ndimage as ndi

def bbox2pts(bbox) :
    x0, y0, x1, y1 = bbox
    return np.array([[[x0,y0]], 
                     [[x1, y0]], 
                     [[x1, y1]], 
                     [[x0, y1]]], np.float32)

class Document:    
    def __init__(self, page_info, template, angle = 0, pad = (0,0,0,0), level = 'word' ) :
        '''
        page info : 
            size : (595, 842),
            color : 'white'
            page_effect : #TODO
            
        
        Template :
            list of contents with properties in [blocks in the page,...]
            
            [{corpus : Corpus object
            block_coord : (x0,y0)
            font : gulim.ttf by default
            space : (word_space, line_space) 가로, 세로}]
        '''
        
        self.page_info = page_info
        self.template = template
        if page_info['page'] != None :
            if os.path.isfile(page_info['page']) :
                page_arr = plt.imread(page_info['page'])
            else :
                bg_select = random.choices([True, False], weights = [0.1, 0.9])[0]
                if bg_select :
                    page_img = random.choice(glob(os.path.join(page_info['page'],'*.jpg')))
                else :
                    page_img = random.choice(glob(os.path.join(page_info['page'], '*.png')))

                page_arr = plt.imread(page_img)
            page_arr = cv2.normalize(page_arr, 0, 255, norm_type = cv2.NORM_MINMAX)
            
            if len(page_arr.shape) == 2 :
                page_arr = np.stack((page_arr,)*3, axis = -1)
            
            self.page = Image.fromarray(np.uint8(page_arr), mode='RGB').resize(page_info['size'])
        else :
            self.page = Image.new('RGB', self.page_info['size'], color = self.page_info['color'])
        self.draw = ImageDraw.Draw(self.page)
        self.angle = angle
        self.bbox = self.get_bbox(level = level)
        self.pad = pad
    # page
    def show_page(self) :
        plt.show()
        plt.figure(figsize = (30,30))
        page = np.array(self.page)
        
        plt.imshow(page)
    
    def clear_page(self) :
        self.page = Image.new('RGB', self.page_info['size'], color = self.page_info['color'])
        self.assign()
        
    def get_page(self) :
        page = np.array(self.page)
        return page

    def assign(self) :
        imtext = Image.new('RGB', self.page.size, 'black')
        drtext = ImageDraw.Draw(imtext)
        for temp in self.template :
            for t in temp.objs :
                drtext.text(t.xy,
                               text = t.get_text(), 
                               font= temp.font, 
                               fill = 'white')
        text_arr = np.array(imtext)
        img_arr = self.get_page()
        img_arr[np.where(text_arr != 0)] = 0
        
        self.page = Image.fromarray(img_arr)

    
    def get_bbox(self, level = 'word') :
        '''
        level = ['corpus', textline', 'word', 'char']
        
        if angle :
            return : text, rotated polygon coordinates
        else : 
            return  : text object
        '''
        bbox_ls = []
        fltred_bbox_ls = []
        if self.angle :
            for temp in self.template :
                if level == 'corpus' :
                    bbox_ls.append((temp.text, self.rotate_bbox(temp, self.angle) ))
                if level == 'textline' :
                    for textline in temp.objs :
                        bbox_ls.append((textline.text, self.rotate_bbox(textline, self.angle)))
                if level == 'word' :
                    for textline in temp.objs :
                        for t in textline.objs :
                            bbox_ls.append((t.text, self.rotate_bbox(t, self.angle)))
                if level == 'char' :
                    for tem in temp.objs :
                        if not isinstance(tem,Anno) :
                            for word in tem.objs :
                                if not isinstance(word,Anno) :
                                    for char in word.chars :
                                        bbox_ls.append((char.text, self.rotate_bbox(char, self.angle) ))

        else :
            for temp in self.template :
                # text lines
                if level == 'corpus' :
                    bbox_ls.append(temp) 
                if level == 'textline' :
                    for textline in temp.objs :
                        bbox_ls.append(textline)
                if level == 'word' :
                    for textline in temp.objs :
                        for t in textline.objs :
                            bbox_ls.append(t)
                if level == 'char' :
                    for tem in temp.objs :
                        if not isinstance(tem,Anno) :
                            for word in tem.objs :
                                if not isinstance(word,Anno) :
                                    for char in word.chars :
                                        bbox_ls.append(char) 
        
        return bbox_ls
    
    def show_bbox(self, level = 'textline') :
        '''
        level = ['corpus', textline', 'word', 'char']
        '''
        if self.angle :
            print('angle : {}'.format(self.angle))
            _ ,bboxes = zip(*self.get_bbox(level = level))
            for bbox in bboxes :
                #TODO: polygon이 안 그려지는 문제
                self.draw.polygon(bbox.flatten().tolist(), fill = None, outline = (0,255, 0))
        else :
            
            for temp in self.template :
                # text lines
                if level == 'corpus' :
                    self.draw.rectangle(temp.bbox, outline = (0,255, 0))
                if level == 'textline' :
                    for textline in temp.objs :
                        self.draw.rectangle(textline.bbox, outline = (0,255,0) )
                if level == 'word' :
                    for textline in temp.objs :
                        for t in textline.objs :
                            self.draw.rectangle(t.bbox, outline = (0,255,0) )
                if level == 'char' :
                    for tem in temp.objs :
                        if not isinstance(tem,Anno) :
                            for word in tem.objs :
                                if not isinstance(word,Anno) :
                                    for char in word.chars :
                                        self.draw.rectangle(char.bbox, outline = (0,255,0) )

      
    
    def rotate(self, angle, level = 'word') : # pad : (top, bottom, left, right)
        # rotate and update bbox coordinates
        self.angle = angle
        
        if self.angle == 0 :
            pass
        top_pad, bottom_pad, left_pad, right_pad = self.pad
        self.page = Image.fromarray(cv2.copyMakeBorder(self.get_page(),
                                       top = top_pad,
                                       bottom = bottom_pad,
                                       left = left_pad,
                                       right = right_pad,
                                       borderType = cv2.BORDER_CONSTANT,
                                       value = (255,255,255)))
        
        w,h = self.page.size                               
        ###
        rot = cv2.getRotationMatrix2D((w/2, h/2) , angle, 1)
        img_arr = self.get_page()

        dst = cv2.warpAffine(img_arr, rot, (0,0), borderMode = cv2.BORDER_REPLICATE)

        dst_pil = Image.fromarray( dst.astype(np.uint8))
        
        self.page = dst_pil
        
        
        
    def rotate_bbox(self,bbox_obj, angle) :
        w,h = self.page.size
        top_pad, bottom_pad, left_pad, right_pad = self.pad
        rot = cv2.getRotationMatrix2D((w/2, h/2) , angle, 1)
        rot_matrix = np.vstack((rot, np.array([0,0,1])))
        bbox = [bbox + bottom_pad if i%2 else bbox+left_pad  for i, bbox in enumerate(bbox_obj.bbox)]
        rotated_bbox = cv2.perspectiveTransform(bbox2pts(bbox), rot_matrix, (0,0))
        return rotated_bbox

    

    def background_effect(self, img) :
        '''
        TODO: blob
        '''
        
        
        effect_dic = {'noise' : noise,
                      'blur' : blur,
                       'motion_blur' : motion_blur,
                      'gaussian_blur' : gaussian_blur,
                      'detail' : detail,
                     }
        
        mode = random.choice(list(effect_dic.keys()))
        
        return effect_dic[mode](img)
        