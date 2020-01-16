## A Page holds rows
# Each row can hold n frames. 
# The frames are added when the row is given a frame_layout


class Page:

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
            #print('updated y_pos for ' + page_row.get_name() + ': '+ str(y_pos))
            page_row.set_y_pos(y_pos)
            page_row.update_frames() #if a row is added, or the rows are modified, all row-frames needs to be updated
    
        # helper
    def get_rows_above_level(self, level):
        rows_above = []
        for page_row in self.rows:
            if page_row.get_level() < level:
                #print(page_row.get_name() + ' is above level ' + str(level))
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
    
    
class Row:
    
    def __init__(self, name, height, level,frame_setup=None):
        self.name = name
        self.height = height
        self.level = level
        self.y_pos = 0
        self.frames = []
        self.frame_setup = frame_setup
        #self.num_columns = num_columns
        if frame_setup is not None:
            self.setup_frames(self.frame_setup)
        
    
    #def get_coordinates()
    # helper
    def setup_frames(self,frame_setup):
        if sum(frame_setup) != 100:
            raise Exception("frame_setup must sum to 100")
        for index,setup in enumerate(frame_setup):
            coordinates = self._add_frame(col_num=index,frame_setup=frame_setup)
            #print(coordinates)
    
    
    def _add_frame(self,col_num,frame_setup):
        from reportlab.rl_config import defaultPageSize
        from reportlab.lib.units import cm
        PAGE_WIDTH=defaultPageSize[0]
        
        if (col_num == 0):
            x_pos_offset = 0
        else:
            x_pos_offset = frame_setup[col_num-1]/100
            
        col_set = {'x': padding+(PAGE_WIDTH-padding*2)*x_pos_offset
               ,'width':((PAGE_WIDTH-padding*2))*(frame_setup[col_num]/100)
               ,'y': self.y_pos
               ,'height':self.height}
        print('frame created in ' + self.get_name())
        self.frames.append(
            Frame(x1=col_set['x'],y1=col_set['y'],
                  width=col_set['width'],height=col_set['height'],
                  leftPadding=0, bottomPadding=0,
                  rightPadding=0, topPadding=6,
                  showBoundary=0)
        )
        return col_set
    
    
    def update_frames_y_pos():
        for index,setup in enumerate(frame_setup):
    
    def update_frames(self):
        self.frames = []
        if self.frame_setup is not None:
            self.setup_frames(self.frame_setup)
            
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
    

