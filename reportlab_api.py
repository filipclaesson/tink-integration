## A Page holds rows
# Each row can hold n frames.
# The frames are added when the row is given a frame_layout

from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import cm
from reportlab.platypus import Frame,Table,Paragraph
from reportlab.lib.colors import pink, black, red, blue, green,white
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import Color
from reportlab.lib.utils import ImageReader
import numpy as np

from reportlab.pdfgen.canvas import Canvas



class Document:

    def __init__(self, name, pagesize=defaultPageSize):
        self.pagesize=pagesize
        self.name=name
        self.canvas = Canvas('mydoc.pdf', pagesize=self.pagesize)
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
    def __init__(self, name,page_number, document,top_padding=2,left_padding=2, background_path=None):
        self.name = name
        self.page_number = page_number
        self.rows = []
        self.document = document
        self.pagesize = self.document.get_pagesize()

        self.document.add_page(self)
        

        self.top_padding=top_padding*cm
        self.left_padding=left_padding*cm

        self.logo_path = None
        self.logo_settings = {}

        self.background_path=background_path

    def get_y_pos_for_level(self,level):
        height_sum = sum([r.get_height() for r in self.rows[:level]]) # sum all 
        return (self.pagesize[1]-self.top_padding)-height_sum
    
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

    def draw_page_elements(self):
        # draw logo
        if self.logo_path is not None:
            logo = ImageReader(self.logo_path)
            if len(self.logo_settings) == 0:
                self.document.get_canvas().drawImage(logo, 10, 10,mask='auto')
            else:
                if self.logo_settings['position']=='bottom-right':
                    y = self.logo_settings['padding']
                    x = float(self.pagesize[0])-logo.getSize()[0]-self.logo_settings['padding']
                    print('x: ' + str(x) + ', y: ' + str(y))
                    self.document.get_canvas().drawImage(logo, y=y, x=x,mask='auto')

    def add_logo(self,logo_path,position,padding):
        self.logo_path = logo_path
        self.logo_settings['position'] = position
        self.logo_settings['padding'] = padding*cm


   
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
        return self.get_page().left_padding + width_sum

    def get_page(self):
        return self.page

    def get_columns(self):
        return self.columns

    def get_y_pos(self):
        return self.y_pos



class Column:

    def __init__(self,name,width,level,row):
        self.name = name
        self.width = width*cm
        self.level = level
        self.row = row
        self.elements = []

        # add the row to the page
        self.row.add_column(self)
        # get the y pos from the page for the current level
        self.x_pos=self.row.get_x_pos_for_level(level) - self.width

        self.frame = Frame(
            x1=self.x_pos, y1=self.row.get_y_pos(),
            width=self.width,height=self.row.get_height(),
            leftPadding=0, bottomPadding=0,
            rightPadding=0, topPadding=6,
            showBoundary=0
        )

    def get_width(self):
        return self.width

    def get_row(self):
        return self.row

    def add_element(self,element):
        self.elements.append(element)

    def draw_elements(self):
        self.frame.addFromList(self.elements, self.get_row().get_page().get_document().get_canvas())




## Separate container for setting up elements
class ComponentHelper():

    def __init__(self):
        self.styles = getSampleStyleSheet()


    def setup_paragraph(self,text,settings):
        from reportlab.lib.styles import ParagraphStyle
        style = ParagraphStyle('test')
        for key in settings:
            style.__dict__[key] = settings[key]
        text_style_added = text
        p = Paragraph(text, style)
        return p


    def setup_table(self, df,totals_line=False,altering_colors=False,red_negative_col=None,formating=[]):
        df_list = np.insert(np.array(df).tolist(), 0, np.array(df.columns.values), axis=0)
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
        
        ## formating
        for inx,l in enumerate(df_list):
            if inx == 0:
                pass
            else:
                for col,format_ in enumerate(formating):
                    if format_ == 'kr':
                        df_list[inx][col] = str(int(float(df_list[inx][col])))+' kr '
                    if format_ == '':
                        pass
        return [style,df_list.tolist()]


## Component helpters
 class Logo:

    


## Example of how to use it
# from reportlab.lib.pagesizes import letter, landscape
# from reportlab.platypus import Image
# from reportlab.lib.units import cm
# ch = rapi.ComponentHelper()
# d = rapi.Document('mydoc.pdf',pagesize=landscape(letter))
# 
# p = rapi.Page("page1",1
#       ,document=d
#       ,top_padding=1.5
#       ,left_padding=4
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
#           ,top_padding=1.5
#           ,left_padding=2
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