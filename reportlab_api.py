## A Page holds rows
# Each row can hold n frames.
# The frames are added when the row is given a frame_layout

from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import cm
from reportlab.platypus import Frame,Table,Paragraph
from reportlab.lib.colors import pink, black, red, blue, green,white
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import Color
import numpy as np


class Page:
    """A page should be added to a Document
   
        Args:
            name: name of the page
            page_numnber: the number of the page
   
   
        Returns:
            Page object
   
    """
    # Initializer / Instance Attributes
    def __init__(self, name, page_number):
        self.name = name
        self.page_number = page_number
        self.rows = []
   
    # updates the y position of all rows
    def update_row_positions(self):
        PAGE_HEIGHT=defaultPageSize[1];
        rows_above = []
        # update all row y-positions (and the frame positions)
        for page_row in self.rows:
            rows_above = self.get_rows_above_level(page_row.get_level())
            height_sum = sum([row.get_height() for row in rows_above])
            y_pos = (PAGE_HEIGHT-3*cm)-height_sum-page_row.get_height()
            
            page_row.set_y_pos(y_pos)
            page_row.update_frames_y_pos() #if a row is added, or the rows are modified, all row-frames needs to be updated
   
        # helper
    def get_rows_above_level(self, level):
        rows_above = []
        for page_row in self.rows:
            if page_row.get_level() < level:
                rows_above.append(page_row)
        return rows_above
       
    def add_row(self,row):
        self.rows.append(row)
        self.update_row_positions()
       
       
    def get_row(self,level):
        return self.rows[level-1]
   
    def get_row_by_name(self,name):
        for i in self.rows:
            if i.get_name() == name:
                return i
   
   
class Row():
    """ A Row should be added to a Page
   
        Args:
            name: name of the row
            height: the height using cm
            level: the level of the row on the row
            frame_setup: array of frame distribution, example: two frames, one taking 2/3 of the space [1/3,2/3]
   
   
        Returns:
            Row object
   
    """
    def __init__(self, name, height, level,frame_setup=None):
        from reportlab.lib.units import cm
        self.name = name
        self.height = height*cm
        self.level = level
        self.y_pos = 0
        self.frames = []
        self.frame_setup = frame_setup
        if frame_setup is not None:
            self.setup_frames(self.frame_setup)
       
   
    #def get_coordinates()
    # helper
    def setup_frames(self,frame_setup):
        if sum(frame_setup) != 100:
            raise Exception("frame_setup must sum to 100")
        for index,setup in enumerate(frame_setup):
            coordinates = self._add_frame(col_num=index,frame_setup=frame_setup)
   
    def _add_frame(self,col_num,frame_setup):
        from reportlab.rl_config import defaultPageSize
        from reportlab.lib.units import cm
        padding=2*cm

        PAGE_WIDTH=defaultPageSize[0]
       
        if (col_num == 0):
            x_pos_offset = 0
        else:
            x_pos_offset = frame_setup[col_num-1]/100
           
        col_set = {'x': padding+(PAGE_WIDTH-padding*2)*x_pos_offset
               ,'width':((PAGE_WIDTH-padding*2))*(frame_setup[col_num]/100)
               ,'y': self.y_pos
               ,'height':self.height}

        ## print('frame created in ' + self.get_name() + ", x: " + str(col_set['x']) + ', y: ' + str(col_set['y']))
        self.frames.append(
            Frame(x1=col_set['x'],y1=col_set['y'],
                  width=col_set['width'],height=col_set['height'],
                  leftPadding=0, bottomPadding=0,
                  rightPadding=0, topPadding=6,
                  showBoundary=0)
        )
        return col_set
   
    def update_frames_y_pos(self):
        for index,setup in enumerate(self.frame_setup):
            ## print("updating frame number " + str(index) + ' in ' + self.name)
            ## print(self.y_pos)
            self.frames[index]._y1 = self.y_pos
            self.frames[index]._y2 = self.y_pos + self.height
            self.frames[index]._reset()

           
    def add_elements_to_frame(self,elements,col_num,canvas):
        self.frames[col_num-1].addFromList(elements,canvas)
       
       
    def get_level(self):
        return self.level
   
    def get_height(self):
        return self.height

    def get_name(self):
        return self.name
   
    def set_y_pos(self,y):
        self.y_pos = y
       
    def get_frame(self,frame_num):
        return self.frames[frame_num-1]






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
        print("test")
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