def set_bbox(bbox) :
    (x0,y0,x1,y1) = bbox
    width = x1 - x0
    height = y1 - y0
    return (x0,y0,x1,y1), (width, height)

class Component :
    
    def __init__(self, text, font, xy) :

        self.text = text
        self.xy = xy
        self.font = font
        self.ascent, self.descent = self.font.getmetrics()

    def get_text(self) :
        return self.text

class Char(Component) :
    def __init__(self, char, font, bbox) :
        assert len(char) == 1
        super().__init__(char, font, bbox[:2])
        self.bbox = bbox
        (self.x0, self.y0, self.x1, self.y1), (self.width, self.height) = set_bbox(self.bbox)
    def __repr__(self) :
        return('<%s text=%r bbox=%s>' \
               % (self.__class__.__name__, self.get_text(), self.bbox))
    
    
class Anno(Component) :
    def __init__(self, char, font, bbox) :
        assert char.strip() == ''
        super().__init__(char, font, bbox[:2])
        self.bbox = bbox
        (self.x0, self.y0, self.x1, self.y1), (self.width, self.height) = set_bbox(self.bbox)
    def __repr__(self) :
        return('<%s text=%r bbox=%s>' \
               % (self.__class__.__name__, self.get_text(), self.bbox))
    
    
class Word(Component) :
    def __init__(self, word, font, xy) :
        super().__init__(word, font, xy)
        width, height = font.getsize(word)
        self.bbox = (self.xy[0], self.xy[1], self.xy[0] + width, self.xy[1] + height)
        self.chars = self.get_charbbox()
        (self.x0, self.y0, self.x1, self.y1), (self.width, self.height) = set_bbox(self.bbox)
        
    def get_charbbox(self) :
        
        x, y = self.xy 
        char_ls = []     
        for i, char in enumerate(self.text) :
            # 띄어쓰기가 아닌 단어
            if char.strip() != '' :
                char_w, char_h = self.font.getsize(char)
                if i+2 < len(self.text) :
                    adj_w = self.cal_kern(''.join(self.text[i:i+2]), self.font)
                    char_w += adj_w
                char_obj = Char(char, self.font, bbox = (x,y, x+char_w, y+char_h))
                char_ls.append(char_obj)
            # 띄어쓰기
            else :
                char_w, char_h = self.font.getsize(char)
                if i+2 < len(self.text) :
                    adj_w = self.cal_kern(''.join(self.text[i:i+2]), self.font)
                    char_w += adj_w
                anno_obj = Anno(char, self.font, bbox = (x,y, x+char_w, y+char_h))
                char_ls.append(anno_obj)
            x += char_w
        return char_ls

    def cal_kern(self, txt, font) :
        t_w, t_h = font.getsize(txt)
        sum_w = 0
        for t in txt :
            c_w, c_h = font.getsize(t)
            sum_w += c_w
        return t_w - sum_w
    
    
    def __getitem__(self, idx) :
        return self.chars[idx]
    
    def __repr__(self) :
        return('<%s text=%r bbox=%s>' \
               % (self.__class__.__name__, self.get_text(), self.bbox))
    
class TextLine(Component) :
    '''
    contains a list of Text objects that represent a single text line
    '''
    def __init__(self, textline, font, xy) :
        super().__init__(textline, font, xy)
        width, height = font.getsize(textline)
        self.bbox = (self.xy[0], self.xy[1], self.xy[0]+width, self.xy[1]+height)
        (self.x0, self.y0, self.x1, self.y1), (self.width, self.height) = set_bbox(self.bbox)
        self.objs = [Word(text, self.font, xy) \
                       if text.strip()!='' \
                       else Anno(text, self.font, xy)\
                       for text, xy in self.get_textbbox(self.text, self.xy)]
        
    def __getitem__(self, idx) :
        return self.objs[idx]
    
    def __repr__(self) :
        return('<%s text=%r bbox=%s>' \
               % (self.__class__.__name__, self.get_text(), self.bbox))
    
    
    def get_textbbox(self, textline, xy) :
        # Anno일때만 bbox return (x0,y0,x1,y1)
        import re
        words = re.split('( )', textline) # 해당 텍스트 라인의 글자를 띄어쓰기로 리스트 분리 (띄어쓰기 포함)
        word_ls = [] # (word, xy)
        start_x = xy[0]
        start_y = xy[1]
        for i, word in enumerate(words) :
            word_w, word_h = self.font.getsize(word)
            if i+2 < len(words) :
                word_gr_w = self.font.getsize(''.join(words[i: i+2]))[0]
                spr_w = self.font.getsize(words[i])[0] + self.font.getsize(words[i+1])[0]
                word_w += (word_gr_w - spr_w)
            x0,y0,x1,y1 = self.font.getbbox(word)
            if word.strip() == '' :
                word_ls.append((word, (start_x, start_y, start_x+ word_w, start_y+ word_h )))
            else :
                word_ls.append((word, (start_x, start_y)))
            end_x = start_x + word_w
            start_x = end_x
        return word_ls

    
    
class Corpus(Component):
    def __init__(self, corpus, font, xy, padding_h, corpus_w, corpus_h, padding_w = 10, align = 'left') : # font 한 글자 기준
        super().__init__(corpus, font, xy)
        self.corpus_w = corpus_w
        self.corpus_h = corpus_h
        self.padding_h = padding_h
        self.padding_w = padding_w
        self.objs = [TextLine(textline, self.font, line_xy) \
                     for textline, line_xy in \
                           self.get_linebbox(corpus = self.text, 
                                             xy = self.xy, 
                                             padding_h = self.padding_h,
                                             padding_w = self.padding_w,
                                             align = align) if textline != '']
                                  
        self.objs = self.adjust_h(self.objs, self.corpus_h, self.font, self.padding_h)
        
        x0s, y0s, x1s, y1s = list(zip(*[line.bbox for line in self.objs]))
        self.bbox = (min(x0s), min(y0s), max(x1s), max(y1s))
        (self.x0, self.y0, self.x1, self.y1), (self.width, self.height) = set_bbox(self.bbox)
        
    ## corpus 사이즈를 벗어나는 줄들 삭제
    def adjust_h(self, obj, corpus_h, font, padding_h) :
        adj_line = int(corpus_h // (font.size + padding_h))
        
        return obj[:adj_line]
    
    def text2lines(self, text, width) :
        line_ls = []
        line = ''
        for t in text :
            line += t
            w, h = self.font.getsize(line)
            if w >= width :
                line_ls.append(line)
                line = ''
        if line != '' :
            line_ls.append(line)
        return line_ls

    
    def get_linebbox(self, corpus, xy, padding_h,  align, padding_w = 0) :

        line_ls = []    
        if align == 'left' :
            lines = self.text2lines(corpus, self.corpus_w - 40) # xy점이 다를 경우 corpus_w 값 수정해서 넣기
            start_x, start_y = xy
            for line in lines :
                line_ls.append((line, (start_x, start_y))) # textline, xy

                start_y += self.font.getsize(line)[1] + padding_h
        elif align == 'center' :
            lines = self.text2lines(corpus, self.corpus_w - padding_w*2)
            start_x, start_y = xy
            for line in lines :
                start_x = (self.corpus_w - self.font.getsize(line)[0] - 2*padding_w)/2 + padding_w
                line_ls.append((line, (start_x, start_y)))
                start_y += self.font.getsize(line)[1] + padding_h
                
        return line_ls
    
    def __getitem__(self, idx) :
        return self.objs[idx]
    
    def __repr__(self) :
        return('<%s text=%r bbox=%s>' \
               % (self.__class__.__name__, self.get_text(), self.bbox))
    
    
