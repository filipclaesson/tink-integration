## A Page holds rows
# Each row can hold n frames.
# The frames are added when the row is given a frame_layout

from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import cm
from reportlab.platypus import Frame,Table,Paragraph,Image,TableStyle,Spacer
from reportlab.lib.colors import pink, black, red, blue, green,white
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.colors import Color
from reportlab.lib.utils import ImageReader
import numpy as np

from reportlab.pdfgen.canvas import Canvas




class Document:

    def __init__(self, name, pagesize=defaultPageSize):
        self.pagesize=pagesize
        self.name=name
        self.canvas = Canvas(name, pagesize=self.pagesize)
        self.pages = []


    def get_canvas(self):
        return self.canvas

    def get_pagesize(self):
        return self.pagesize

    def add_page(self,page):
        self.pages.append(page)

    def save(self):
        for page in self.pages:
            page.draw_page_elements()
            for row in page.get_rows():
                for column in row.get_columns():
                    #print('drawing ' + column.name)
                    column.draw_elements()
            print('page ' + str(page.page_number) + ' complete')
            self.canvas.showPage()

        self.canvas.save()


class Page:
    """A page should be added to a Document
   
        Args:
            name: name of the page
            page_numnber: the number of the page
   
   
        Returns:
            Page object
   
    """
    # Initializer / Instance Attributes
    def __init__(self, name,page_number, document,y_padding=2,x_padding=2, background_path=None):
        self.name = name
        self.page_number = page_number
        self.rows = []
        self.document = document
        self.pagesize = self.document.get_pagesize()

        self.document.add_page(self)
        
        self.y_padding=y_padding*cm
        self.x_padding=x_padding*cm

        self.logo = None
        self.background_path=background_path

    def get_y_pos_for_level(self,level):
        height_sum = sum([r.get_height() for r in self.rows[:level]]) # sum all 
        return (self.pagesize[1]-self.y_padding)-height_sum
    
    ## TODO: error handling, should not be able to add more rows than max pange height   
    def add_row(self,row):
        self.rows.append(row)

   
    def get_row_by_name(self,name):
        for i in self.rows:
            if i.get_name() == name:
                return i

    def get_rows(self):
        return self.rows

    def get_document(self):
        return(self.document)

    def get_padding(self):
        return {'x_padding':self.x_padding,'y_padding':self.y_padding}

    def draw_page_elements(self):
        if self.logo is not None:
            self.logo.draw()

    def add_logo(self,logo):
        self.logo = logo


   
class Row:
    """ A Row should be added to a Page
   
        Args:
            name: name of the row
            height: the height using cm
            level: the level of the row on the row
            frame_setup: array of frame distribution, example: two frames, one taking 2/3 of the space [1/3,2/3]
   
        Returns:
            Row object
   
    """
    def __init__(self, name, height, level, page,frame_setup=None, row_width=defaultPageSize[0]):
        self.name = name
        self.height = height*cm
        self.level = level
        self.page = page
        self.columns=[]

        # add the row to the page
        self.page.add_row(self)
        # get the y pos from the page for the current level
        self.y_pos=self.page.get_y_pos_for_level(level)

    ## TODO: error handling, should not be able to add more columns than max pange width
    def get_height(self):
        return self.height

    def add_column(self,column):
        self.columns.append(column)

    def get_x_pos_for_level(self,level):
        width_sum = sum([c.get_width() for c in self.columns[:level]]) # sum all 
        # max_width = self.get_page().pagesize[0]
        return self.get_page().x_padding + width_sum

    def get_page(self):
        return self.page

    def get_columns(self):
        return self.columns

    def get_y_pos(self):
        return self.y_pos



class Column:

    def __init__(self,name,width,level,row,show_boundry=0,padding_left=0):
        self.name = name
        self.width = width*cm
        self.level = level
        self.row = row
        self.elements = []
        self.padding_left = padding_left*cm
        

        # add the row to the page
        self.row.add_column(self)
        # get the y pos from the page for the current level
        self.x_pos=self.row.get_x_pos_for_level(level) - self.width
        self.y_pos=self.row.get_y_pos() 
        #print('init column ' + self.name + ', x_pos: ' + str(self.x_pos) + ', y_pos: ' + str(self.y_pos))

        self.frame = Frame(
            x1=self.x_pos, y1=self.row.get_y_pos(),
            width=self.width,height=self.row.get_height(),
            leftPadding=0, bottomPadding=0,
            rightPadding=0, topPadding=6,
            showBoundary=show_boundry
        )

    def get_width(self):
        return self.width+self.padding_left

    def get_row(self):
        return self.row

    def get_frame(self):
        return self.frame

    def add_element(self,element):
        self.elements.append(element)

    def draw_elements(self):
        for e in self.elements:
            e.draw()








########################################
##                                    ##
##                                    ##
##              Components            ##
##                                    ##
##                                    ##
########################################
class Component:
    def __init__(self, name):
        self.name=name



class ColumnComponent(Component):
    def __init__(self, name, column):
        super().__init__(name)
        self.column = column
        self.column.add_element(self)


    def draw(self):
        # NOTE THAT THE self.platypus_object is defined in the children
        self.column.get_frame().addFromList([self.platypus_object], self.column.get_row().get_page().get_document().get_canvas())

class ColImage(ColumnComponent):
    def __init__(self,name,column,path,width=None,height=None):
        super().__init__(name,column)
        img = ImageReader(path)
        iw, ih = img.getSize()
        aspect = ih / float(iw)
        if width is None:
            width = aspect*2
        if height is None:
            height=(width * aspect)
        
        self.platypus_object = Image(path, width=width, height=height, hAlign='LEFT')

class ColParagraph(ColumnComponent):
    
    def __init__(self,name,column,text,text_settings):
        super().__init__(name,column)
        style = ParagraphStyle('test')
        for key in text_settings:
            style.__dict__[key] = text_settings[key]
        self.platypus_object = Paragraph(text,style)

class ColSpacer(ColumnComponent):
    
    def __init__(self,name,column,x,y):
        super().__init__(name,column)
        self.platypus_object = Spacer(x,y)

class ColTable(ColumnComponent):

    def __init__(self,name,column,df,totals_line=False,altering_colors=False,red_negative_col=None,formating=[]):
        super().__init__(name,column)
        self.setup_table(df,totals_line,altering_colors,red_negative_col,formating)
        
        table = Table(self.df);
        table.setStyle(TableStyle(self.style))

        self.platypus_object = table


    def setup_table(self, df,totals_line=False,altering_colors=False,red_negative_col=None,formating=[]):
        df_list = np.insert(np.array(df).tolist(), 0, np.array(df.columns.values), axis=0)
        df_list = df_list.astype('U140', copy=False)
        tot_cols = df.shape[1]-1
        style=[]
        style.append(('TEXTCOLOR',(0,0),(tot_cols,0),black))
        style.append(('BACKGROUND',(0,0),(tot_cols,0),white))#reportlab.lib.colors.Color(110/255, 110/255, 110/255)))
        style.append(('FONTNAME', (0,0), (tot_cols,0), 'Courier-Bold'))
        style.append(('LINEABOVE', (0,1), (tot_cols,1), 1, black))
        
        for i in range(1,len(df_list)):
            style.append(('FONTNAME', (0,i), (tot_cols,i), 'Courier'))
            style.append(('ALIGN', (1,i), (tot_cols,i), 'RIGHT'))
        
        ## altering colors
        if altering_colors:
            for i in range(1,len(df_list)):
                if i%2 == 1: 
                    text_col=black
                    background_col=Color(240/255, 240/255, 240/255)
                else:
                    text_col=black
                    background_col=Color(255/255, 255/255, 255/255)
                    
                style.append(('TEXTCOLOR',(0,i),(tot_cols,i),text_col))
                style.append(('BACKGROUND',(0,i),(tot_cols,i),background_col))
                #style.append(('FONTNAME', (0,i), (1,i), 'Courier'))
        
        ## totals line
        if totals_line:
            style.append(('LINEABOVE',(0,len(df_list)-1),(len(df_list)-1,3), 1, black))
            
        ## red negative
        if red_negative_col is not None:
            for idx, val in (df.iterrows()):
                if(val[red_negative_col-1]<0):
                    style.append(('TEXTCOLOR',(0,idx+1),(tot_cols,idx+1),red))
        #style.append(('ALIGN', (1,1), (-1,-1), 'RIGHT'))
        ## formating
        for inx,l in enumerate(df_list):
            if inx == 0:
                pass
            else:
                for col,format_ in enumerate(formating):
                    
                    if format_ == 'kr':
                        df_list[inx][col] = str(int(float(df_list[inx][col])))+' kr'
                        
                    

                    if format_ == '':
                        pass


        self.df = df_list.tolist()
        self.style = style
        return [style,df_list.tolist()]

    
        
## Logo är inte en del av columnerena utan ritas separat
class Logo(Component):
    def __init__(self, name, path, page, width, height, position, padding):
        super().__init__(name)
        self.path = path
        self.page = page
        self.width = width
        self.height = height
        self.padding = padding*cm
        self._set_postition_from_text(position)
        self.page.add_logo(self)

    def draw(self):
        self.page.get_document().get_canvas().drawImage(self.path, self.x, self.y,mask='auto')

    def _set_postition_from_text(self, position_text):
        if position_text.split('-')[0]=='bottom':
            self.y = self.padding
        if position_text.split('-')[0]=='top':
            self.y = self.page.get_document().get_pagesize()[1]- self.padding - self.width
        if position_text.split('-')[1]=='left':
            self.x = self.padding
        if position_text.split('-')[1]=='right':
            self.x = self.page.get_document().get_pagesize()[0]-self.width-self.padding

        #print('x: ' + str(self.x) + ', y: ' + str(self.y))


########################################
##                                    ##
##                                    ##
##           How to use it            ##
##                                    ##
##                                    ##
########################################





## Example of how to use it
# from reportlab.lib.pagesizes import letter, landscape
# from reportlab.platypus import Image
# from reportlab.lib.units import cm
# ch = rapi.ComponentHelper()
# d = rapi.Document('mydoc.pdf',pagesize=landscape(letter))
# 
# p = rapi.Page("page1",1
#       ,document=d
#       ,y_padding=1.5
#       ,x_padding=4
#      )
# r1 = rapi.Row(name="header1",height=7,level=1,page=p)
# r1_c1 = rapi.Column(name="r1c1",width=10,level=1,row=r1)
# r1_c2 = rapi.Column(name="r1c1",width=10,level=2,row=r1)
# r2 = rapi.Row(name="header1",height=7,level=2,page=p)
# r2_c1 = rapi.Column(name="r1c1",width=10,level=1,row=r2)
# r2_c2 = rapi.Column(name="r1c1",width=10,level=2,row=r2)
# 
# im = Image("./plots/"+plots[0], width=8*cm, height=6*cm)
# r1_c1.add_element(im)
# im = Image("./plots/"+plots[0], width=8*cm, height=6*cm)
# r2_c2.add_element(im)
# d.save()
# 
# ## with loop
# from reportlab.lib.pagesizes import letter, landscape
# from reportlab.platypus import Image
# from reportlab.lib.units import cm
# ch = rapi.ComponentHelper()
# d = rapi.Document('mydoc.pdf',pagesize=landscape(letter))
# 
# import math
# for page in range(0,math.ceil(len(plots)/4)):
#     p = rapi.Page("page1",page
#           ,document=d
#           ,y_padding=1.5
#           ,x_padding=2
#          )
#     r1 = rapi.Row(name="header1",height=7,level=1,page=p)
#     r1_c1 = rapi.Column(name="r1c1",width=10,level=1,row=r1)
#     r1_c2 = rapi.Column(name="r1c1",width=10,level=2,row=r1)
#     r2 = rapi.Row(name="header1",height=7,level=2,page=p)
#     r2_c1 = rapi.Column(name="r1c1",width=10,level=1,row=r2)
#     r2_c2 = rapi.Column(name="r1c1",width=10,level=2,row=r2)
#     
#     r1_c1.add_element(Image("./plots/"+plots[0+page*4-1], width=8*cm, height=6*cm))
#     r1_c2.add_element(Image("./plots/"+plots[1+page*4-1], width=8*cm, height=6*cm))
#     r2_c1.add_element(Image("./plots/"+plots[2+page*4-1], width=8*cm, height=6*cm))
#     r2_c2.add_element(Image("./plots/"+plots[3+page*4-1], width=8*cm, height=6*cm))
# d.save()
# 