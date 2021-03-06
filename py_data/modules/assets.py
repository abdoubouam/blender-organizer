# -*- coding: utf-8 -*-

# system
import os
import socket

# graphics interface
import gtk
import pango
import cairo
import glib
try: 
    import Image
except:
    from PIL import Image

# calculational help
import datetime


# self made modules

import thumbnailer
import checklist
import dialogs
import fileformats

#### AN ASSET IS AN OBJECT THAT WILL HOLD INFORMATION ABOUT A PARTICULAR ASSET
#    IN THE PROJECT
#    IT'S PERSENTAGE, NAME, PREVIEW PIC, etc....
class asset:
    def __init__(self, pf, path, CUR, name):
        
        self.pf = pf
        self.path = path
        self.name = name
        self.CUR = CUR
        
        
        #making sure all NESSESARY FOLDERS ARE IN THE DIRECTIORY
        
        # tex, reference, renders
        
        try:
            os.mkdir(path+"/tex") 
            os.mkdir(path+"/renders")
            os.mkdir(path+"/reference")
        
        except:
            pass
        
        # now the nessesary files
        # blend, asset.progress
        
        # asset.progress
        if os.path.exists(path+"/asset.progress") == False:
            o = open("py_data/new_file/asset.progress", "r")
            w = open(path+"/asset.progress", "w")
            w.write(o.read())
            w.close()
        # blend file
        if os.path.exists(path+"/"+name+".blend") == False:
            o = open("py_data/new_file/empty.blend", "r")
            w = open(path+"/"+name+".blend", "w")
            w.write(o.read())
            w.close()
        
        
        
        
        ###### READING DATA  #####
        
        
        
        # checking if the item is finished...
        # looking into the ast folder instead of dev
        
        
        self.done = self.name+".blend" in os.walk(self.pf+"/ast/"+CUR).next()[2]
        
            
        # getting the persentage from the checklist
        
        self.percent = checklist.partcalculate(checklist.openckecklist(path+"/asset.progress"))
        
        if self.done:
            self.percent = 1.0 # just making sure
            
        
        # getting the icon
        
        
        if os.path.exists(self.path+"/renders/Preview.jpg"):
            self.pic = thumbnailer.thumbnail(self.path+"/renders/Preview.jpg", 100, 100)
            self.pic = gtk.gdk.pixbuf_new_from_file(self.pic)
            self.preview = thumbnailer.thumbnail(self.path+"/renders/Preview.jpg", 400, 400)
            self.preview = gtk.gdk.pixbuf_new_from_file(self.preview)
            
        else:
            self.pic = self.pf+"/py_data/icons/"+CUR+"_prev.png"
            self.pic = gtk.gdk.pixbuf_new_from_file(self.pic)
            
            self.preview = self.pic
        
        
        # getting the asset /ast/ if it's finished
        if self.done:
            astpath = self.pf+"/ast/"+self.CUR+"/"+self.name+".blend"
            print astpath
            
            
            
            
            try:
                astpic = thumbnailer.blenderthumb(astpath, 100, 100)
                astpic = gtk.gdk.pixbuf_new_from_file(astpic)
                
            except:
                astpic = self.pf+"/py_data/icons/blendfile_big.png"
                astpic = gtk.gdk.pixbuf_new_from_file(astpic)
            
            self.ast = [astpic, astpath]
        else:
            self.ast = [None, None]
        
        
        
    def info(self):
        
        return {
                "PATH:": self.path,
                "NAME:": self.name ,
                "DIRE:": self.CUR,
                "DONE:": self.done,
                "PERS:": self.percent
                }
    

####   ACTUALL DRAWING OF THE DIALOG ( WITH DRAWABLE BECAUSE WHY NOT )
class draw_assets:
    
    def __init__(self, pf, box, win, CUR):
    
        self.pf = pf # pf stands for project folder. It's a string to know
                     # where the project's folders start with
        
        self.box = box # the gtk.Box() container to put this widget into
        
        self.win = win
        self.CUR = CUR
        
        self.assets = []
        
        
        ## THIS IS WHERE THE READING OF THE FOLDER HAPPENDS
        
        self.folder_read()
        
        
        
        
        
        
        # PREPARATION TO DRAW
        
        self.screen = "selection"
        self.allowed = True
        
        self.scroll = 0
        #in item scrolls
        self.iscroll = [0,0,0]
        self.blscroll = 0
        
        self.dW = 0
        self.DH = 0
        
        self.mpx = 0
        self.mpy = 0
        self.mpf = None
        
        self.newitem = None # Placeholder for a name of the new item if such created
        self.justadded = False
        
        
        # ICONS
        self.donepic = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/"+CUR+"_asset_done.png")
        self.undonepic = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/"+CUR+"_asset_undone.png")
        self.rendericon = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/pic.png")
        self.foldericon = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/folder.png")
        self.checklisticon = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/checklist.png")
        self.editicon = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/edit.png")
        self.blendericon = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/blender.png")
        self.blendfileicon = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/blendfile_big.png")
        self.okicon = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/ok.png")
        self.fade_01 = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/INT/fade_01.png")
        self.fade_02 = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/INT/fade_02.png")
        self.fade_03 = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/INT/fade_03.png")
        self.fade_04 = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/INT/fade_04.png")
        
        self.iteminfo = None
        self.blends = None
        
        def framegraph(widget, event):
                                                    
            w, h = widget.window.get_size()
            xgc = widget.window.new_gc()
            
            mx, my, fx  = widget.window.get_pointer()
            
            
            # GETTING WHETHER THE WINDOW IS ACTIVE
            
            self.winactive = win.is_active()
            

                
            
            
            
            ctx = widget.window.cairo_create()
            ctx.select_font_face("Sawasdee", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            
            xgc.line_width = 2
            
            # BACKGROUND COLOR
            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#868686")) ## CHOSE COLOR
            widget.window.draw_rectangle(xgc, True, 0, 0, w, h)  ## FILL FRAME    
            
            
            inthescreen = False
            if my > 50:
                inthescreen = True
            
            
            
            
            mouseoverany = False
            
            #### SELECTION ITEM SCREEN
            if self.screen == "selection":
                
                #widget.set_size_request(500,500)
                
                
                
                
                
                
                
                
                
                # SELECTABLE CELLLS
                
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#9F8b78"))
                if "GDK_BUTTON1" in str(fx) and self.allowed and "GDK_BUTTON1" not in str(self.mpf) and win.is_active():
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#555"))
                
                
                #widget.window.draw_rectangle(xgc, True, mx/200*200, (my+self.scroll)/200*200-self.scroll, 200, 200)
                
            
                try:
                    avarage = self.assets[0].percent
                except:
                    avarage = 0.0
                
                
                ### CELLS
                
                
                
                xc = 0
                yc = 0
                
                
                ############# CELLS DRAING  ##################
                
                
                for x, i in enumerate(self.assets):
                    
                    nx = xc*200
                    ny = yc*200-self.scroll+50
                    
                    
                    # NEW ITEM ( in case it was just created )
                    
                    if i.name == self.newitem:
                        
                        xgc.set_rgb_fg_color(gtk.gdk.color_parse("#aaa"))
                        widget.window.draw_rectangle(xgc, True, nx, ny, 200, 200)
                    
                        #adjust the scroll
                        
                        
                        if self.justadded:
                            self.scroll = ny*200
                            self.justadded = False
                        
                        
                      
                     
                    ### MOUSE OVER
                    
                    mouseover = False
                    if mx > nx and mx < nx+200 and my > ny and my < ny+200 and inthescreen:
                        
                        
                        mouseover = True
                        mouseoverany = True
                        xgc.set_rgb_fg_color(gtk.gdk.color_parse("#e47649"))
                        
                        ## MOUSE PRESSED
                        
                        if "GDK_BUTTON1" in str(fx) and self.allowed and "GDK_BUTTON1" not in str(self.mpf) and win.is_active() and inthescreen:
                            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#000"))
                            
                            
                            widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
                            
                            
                
                            while gtk.events_pending():
                                gtk.main_iteration()
                            
                            self.blends = self.loadBlendFiles(i)
                            self.iteminfo = self.loaditem(i)
                            self.screen = i
                            
                        widget.window.draw_rectangle(xgc, True, nx, ny, 200, 200)
                        
                        xgc.set_rgb_fg_color(gtk.gdk.color_parse("#4c4c4c"))
                        
                        
                        
                        xgc.line_width = 4
                        widget.window.draw_rectangle(xgc, False, nx, ny, 200, 200)
                        xgc.line_width = 2
                    
                       
                        
                    
                    # little icon
                    # nod to the original design
                    self.donepic
                    
                    if i.done:
                        widget.window.draw_pixbuf(None, self.donepic, 0, 0, nx+2, ny+2, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
                    else:
                        widget.window.draw_pixbuf(None, self.undonepic, 0, 0, nx+2, ny+2, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)     
                            
                    # name
                    
                    ctx.set_font_size(15)
                    ctx.move_to( nx+33, ny+20)
                    ctx.show_text(i.name[:15])
                    ctx.move_to( nx+33, ny+40)
                    ctx.show_text(i.name[15:])
                    
                    
                    # preview draw
                    
                    yoffset = (100-i.pic.get_height())/2 # get_width
                    xoffset = (100-i.pic.get_width())/2
                    
                    
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#727272"))
                    widget.window.draw_rectangle(xgc, True, nx+50, ny+50, 100, 100)
                    
                    
                    widget.window.draw_pixbuf(None, i.pic, 0, 0, nx+50+xoffset, ny+50+yoffset, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
                    
                    
                    # percentage widget
                    
                    
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#000"))
                    
                    widget.window.draw_rectangle(xgc, False, nx+10, ny+180, 180, 10)
                    
                    avarage = (avarage + i.percent)/2
                    
                    
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#db3c16"))
                    if mouseover:
                        xgc.set_rgb_fg_color(gtk.gdk.color_parse("#4c4c4c"))
                    widget.window.draw_rectangle(xgc, True, nx+12, ny+182, int(176*i.percent), 6)
                    
                    ctx.set_font_size(10)
                    ctx.move_to( nx+10, ny+175)
                    ctx.show_text(str(int(i.percent*100))+" %")
                     
                    
                        
                    
                    ### SAVING TO THE NEXT ONE
                    if i != self.assets[-1]:
                    
                        if xc + 1 > w/200-1:
                            xc = 0
                            yc = yc + 1
                        else:
                            xc = xc + 1
                    
                        
                
                 
                
                
                
                    
                ### SCROOL ###
                
                # the scroll is done with the middle mouse button
                if self.mpy > my and "GDK_BUTTON2" in str(fx) and "GDK_BUTTON2" in str(self.mpf):
                    
                    self.scroll = self.scroll + (self.mpy-my)
                
                if self.mpy < my and "GDK_BUTTON2" in str(fx) and "GDK_BUTTON2" in str(self.mpf):
                    
                    self.scroll = self.scroll - (my-self.mpy)
               
                
                
                
                
                
                pixtdall = (yc+1)*200-h+50
                
                if self.scroll > pixtdall:
                    self.scroll = pixtdall
                
                if self.scroll < 0:
                    self.scroll = 0
                
                
                ## top pannel
                
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#727272")) ## CHOSE COLOR
                widget.window.draw_rectangle(xgc, True, 0, 0, w, 50)
                     
                
                # BIG PERCENTAGE BAR FOR THE ENTIRE CATEGORY
                ctx.set_font_size(20)
                ctx.move_to( 100, 30)
                ctx.show_text(str(int(avarage*100))+" %")
                
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#000")) ## CHOSE COLOR
                widget.window.draw_rectangle(xgc, False, 200, 5, w-210, 40)
                
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#3c3c3c"))
                
                widget.window.draw_rectangle(xgc, True, 202, 7, int((w-206)*avarage), 36)
                
                
                
                #### ADD BUTTON
                
                plus = [(20,10),(20,20),(10,20),(10,30),(20,30),(20,40),(30,40),(30,30),(40,30),(40,20),(30,20),(30,10)]
                
                if mx > 10 and my > 10 and mx < 40 and my < 40:
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#e47649"))
                    if "GDK_BUTTON1" in str(fx) and self.allowed and "GDK_BUTTON1" not in str(self.mpf) and win.is_active():
                        xgc.set_rgb_fg_color(gtk.gdk.color_parse("#000"))
                        
                        
                        # just incase all freezes
                        xgc.set_rgb_fg_color(gtk.gdk.color_parse("#3c3c3c"))    
                        xgc.line_width = 2
                        widget.window.draw_polygon(xgc, False, plus)
                        
                        # RUNNING THE DIALOG
                        
                        glib.timeout_add(20, self.call_add_dialog)
                        
                        
                    
                    widget.window.draw_polygon(xgc, True, plus)
                    
                    
                    # TOOLTIP
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#aaa"))   
                    widget.window.draw_rectangle(xgc, True, mx+20, my+5, 200, 20)
                    ctx.set_font_size(15)
                    ctx.move_to( mx+30, my+20)
                    ctx.show_text("ADD NEW ITEM")
                    
                    
                    
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#3c3c3c"))    
                xgc.line_width = 2
                widget.window.draw_polygon(xgc, False, plus)
                
                
                
                
                
                
                
                
                ## scroller
                
                pixtdall = (yc+1)*200
                
                
                scs = int ( 70+ (float((h-70))/pixtdall*(self.scroll ) ) )   # IF YOU TOUCH THAT CODE I GONNA FUCK YOU AND YOUR FAMILY
                scf = int ( (float((h-70))/pixtdall*(    h-50 ) )) + scs -20 # DON'T EVEN FUCKING DARE... THIS WAS A NIGHTMARE
                
                if scf < h-19: 
                    
                
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#727272")) 
                    widget.window.draw_line(xgc, w-20, 70, w-20, h-20)  ### SCROLL LINE
                    
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#000"))
                    widget.window.draw_line(xgc, w-20, scs, w-20, scf)  ### SCROLLER
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            ###### IF ITEM SELSECTED
            
            
            
            
            else: # to the if self.screen = "select"
                
                ctx.set_source_rgb(1,1,1)
                #widget.set_size_request(500,900)
                
                
                
                mmx = self.screen.preview.get_width()
                mmy = self.screen.preview.get_height()
                
                
                
                
                
                
                
                
                
                
                
                ##### IMAGES IN THE renders, tex, reference FOLDERS ####
                
                
                
                
                
                
                
                rawnames = ["RENDERS", "TEXTURES", "REFERENCES"]
                rawdirs = ["renders", "tex","reference"]
                
                
                
                        
                
                
                #basic math to get the sizes of stuff
                
                raws = len(self.iteminfo) #how much raws
                                          # so far it's like 3
                                          # look def loaditem():
                
                
                margin = 10 # space between raws
                
                raw_true_w = (w / raws)
                raw_w = (w / raws) - (margin * 2) # getting the width of the raw
                
                raw_start = mmy + 170 # starting height
                raw_h = h - raw_start # height
                
                
                for raw, data in enumerate(self.iteminfo):  # stating the loop of 3 raws
                    
                    # a little more math
                    the_raw_w_start = raw_true_w*raw+10
                    
                    # raws frames
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#5c5c5c")) ## CHOSE COLOR
                    widget.window.draw_rectangle(xgc, True, the_raw_w_start , raw_start, raw_w, raw_h)
                    
                    
                    ## IMAGES ##
                    
                    ix = 0
                    iy = 0
                    
                    
                    mouseinraw = False
                    if my in range( raw_start, h ) and mx in range( the_raw_w_start, the_raw_w_start+raw_w  ):
                        mouseinraw = True   
                        
                    
                    
                    for ind, render in enumerate(data): # look to the previous indentantion
                                                        # for the data reference
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        ### MATH ###
                        
                        
                        center_X = (100-render[0].get_width())/2
                        center_Y = (100-render[0].get_height())/2 # GETTING THE PICTURE TO THE CENTER IN RELATION TO It'S SIZE
                        
                    
                        
                        mox = ix*100 + the_raw_w_start + ix*10 + 10 
                        moy = iy*100 + raw_start + iy*10       + 10 + self.iscroll[raw] 
                        
                        
                        imx = mox   + center_X
                        imy = moy   + center_Y
                        
                        
                        mouseover = False
                        
                        #### MOUSE OVER ####
                        
                        if mx > mox and mx < mox+100 and my > moy and my < moy+100 and mouseinraw:
                            mouseover = True
                            mouseoverany = True
                            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#e47649"))
                            
                            
                            widget.window.draw_rectangle(xgc, True, mox-5, moy-5, 110, 110)
                            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#4c4c4c"))
                            
                            
                            
                            xgc.line_width = 4
                            widget.window.draw_rectangle(xgc, False, mox-5, moy-5, 110, 110)
                            xgc.line_width = 2
                            
                            # IF CLICKED
                            if "GDK_BUTTON1" in str(fx) and self.allowed and "GDK_BUTTON1" not in str(self.mpf) and win.is_active():
                                
                                os.system("xdg-open "+render[1])
                        
                        
                        
                        
                        ### DRAWING
                        
                        if not mouseover:
                            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#393939"))
                            widget.window.draw_rectangle(xgc, True, mox, moy, 100, 100)
                        
                        
                        widget.window.draw_pixbuf(None, render[0], 0, 0, imx, imy, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)
                        
                        # text ( the picture filename )
                        
                        ctx.set_font_size(10)
                        
                        if mouseover:
                            ctx.set_font_size(20)
                        
                        ctx.move_to( mox, moy + 108)
                        ctx.show_text(render[2][:15])
                        
                        
                        # TO THE NEXT FRAME
                        ix = ix + 1
                        if (ix * 100 + ix*10) > raw_w-120:
                            iy = iy + 1
                            ix = 0
                    
                    
                    
                    ### SCROLL ###
                        
                    if mouseinraw:
                        
                        if self.mpy > my and "GDK_BUTTON2" in str(fx) and "GDK_BUTTON2" in str(self.mpf):
                            
                            
                            self.iscroll[raw] = self.iscroll[raw] + (my-self.mpy)
                        
                        if self.mpy < my and "GDK_BUTTON2" in str(fx) and "GDK_BUTTON2" in str(self.mpf):
                            
                            self.iscroll[raw] = self.iscroll[raw] - (self.mpy-my) 
                        
                        
                    Yinpix = raw_h+(iy*100 + iy*10)*-1-120
                        
                    if self.iscroll[raw] < Yinpix:
                        self.iscroll[raw] = Yinpix
                        
                    if self.iscroll[raw] > 0:
                        self.iscroll[raw] = 0
                    
                    
                    
                    ## scrolled indicator ###
                    
                    # fade 03
                    
                    if self.iscroll[raw] < 0:
                        widget.window.draw_pixbuf(None, self.fade_03, 0, 0, the_raw_w_start, raw_start, raw_w, 40, gtk.gdk.RGB_DITHER_NONE, 0, 0)
                    
                    if (iy*100 + iy*10)+130 > raw_h and Yinpix != self.iscroll[raw]:
                        widget.window.draw_pixbuf(None, self.fade_04, 0, 0, the_raw_w_start, h-40, raw_w, 40, gtk.gdk.RGB_DITHER_NONE, 0, 0)
                    
                    
                    
                    
                    
                    
                    
                    
                    # CLEANING #
                    
                    
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#868686")) ## CHOSE COLOR
                    widget.window.draw_rectangle(xgc, True, raw_true_w*raw, 50, raw_true_w, raw_start-50)
                    
                    # tab thingy
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#5c5c5c")) ## CHOSE COLOR
                    widget.window.draw_rectangle(xgc, True, the_raw_w_start+10 , raw_start-30, 200, 30)
                    
                    
                    # tab icons
                    
                    widget.window.draw_pixbuf(None, self.rendericon, 0, 0, the_raw_w_start+14, raw_start-28, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)
                    
                    
                    # teb name
                    
                    ctx.set_font_size(20)
                    ctx.set_source_rgb(1,1,1)
                    ctx.move_to( the_raw_w_start+14+30, raw_start-10)
                    ctx.show_text(rawnames[raw])
                
                
                    # foldrer button
                    
                    icon_x = the_raw_w_start+180
                    icon_y = raw_start-28
                    icon_s = 22
                    
                    
                    ### MOUSE OVER
                    if mx > icon_x and mx < icon_x+icon_s and my > icon_y and my < icon_y+icon_s:
                        
                        mouseoverany = True
                        xgc.set_rgb_fg_color(gtk.gdk.color_parse("#e47649"))
                        widget.window.draw_rectangle(xgc, True, icon_x, icon_y, icon_s, icon_s)
                        
                        
                        
                        
                        # IF CLICKED
                        if "GDK_BUTTON1" in str(fx) and self.allowed and "GDK_BUTTON1" not in str(self.mpf) and win.is_active():
                            
                            os.system("nautilus "+self.pf+"/dev/"+self.CUR+"/"+self.screen.name+"/"+rawdirs[raw])
                        
                        
                        
                        
                     
                    widget.window.draw_pixbuf(None, self.foldericon, 0, 0, icon_x, icon_y, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)
                
                
                
                
                
                
                
                        
                
                
                
                
                
                
                
                
                
                
                
                
                
                ######### BLEND FILES
                
                
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#5c5c5c")) ## CHOSE COLOR
                widget.window.draw_rectangle(xgc, True, 0, mmy-15, w, 115)
                widget.window.draw_rectangle(xgc, True, mmx+140, mmy-45, 200, 100)
                
                #blender icon
                widget.window.draw_pixbuf(None, self.blendericon, 0, 0, mmx+144, mmy-41, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)
                
                
                ctx.set_font_size(20)
                ctx.set_source_rgb(1,1,1)
                ctx.move_to( mmx+172, mmy-24)
                ctx.show_text("BLEND FILES")
                
                
                #### SCROLL OF BLEN FILES ####
                
                
                
                if my > mmy-12 and my < mmy-12+100 and mx > mmx + 117+110:
                    
                    if self.mpx > mx and "GDK_BUTTON2" in str(fx) and "GDK_BUTTON2" in str(self.mpf):
                        
                        
                        self.blscroll = self.blscroll + (mx-self.mpx)
                    
                    if self.mpx < mx and "GDK_BUTTON2" in str(fx) and "GDK_BUTTON2" in str(self.mpf):
                        
                        
                        self.blscroll = self.blscroll - (self.mpx-mx)
                
                if self.blscroll < (w-(mmx+117+110))+(len(self.blends)*110+60)*-1:
                        self.blscroll = (w-(mmx+117+110))+(len(self.blends)*110+60)*-1
                    
                if self.blscroll > 0:
                    self.blscroll = 0    
                
                
                
                
                for num, blend in enumerate(self.blends):
                
                    
                    
                    ### MOUSE OVER
                    
                    if mx > mmx + 117+110 and mx > mmx + 117+110 +(num*110)+self.blscroll and mx < mmx + 117+110 +(num*110)+self.blscroll+100 and my > mmy-12 and my < mmy-12+100:
                        mouseoverany = True
                        
                        xgc.set_rgb_fg_color(gtk.gdk.color_parse("#e47649"))
                        widget.window.draw_rectangle(xgc, True, mmx + 115+110 +(num*110)+self.blscroll, mmy-14, 104, 104)
                        
                        xgc.set_rgb_fg_color(gtk.gdk.color_parse("#4c4c4c"))
                        
                        xgc.line_width = 4
                        widget.window.draw_rectangle(xgc, False, mmx + 115+110 +(num*110)+self.blscroll, mmy-14, 104, 104)
                        xgc.line_width = 2
                        
                        # IF CLICKED
                        if "GDK_BUTTON1" in str(fx) and self.allowed and "GDK_BUTTON1" not in str(self.mpf) and win.is_active():
                            
                            os.system("xdg-open "+blend[1])
                
                    #BLEND PREVIEW 
                    widget.window.draw_pixbuf(None, blend[0], 0, 0, mmx + 117 +110 +(num*110)+self.blscroll, mmy-12, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)
                    
                    ctx.set_font_size(10)
                        
                    ctx.move_to(mmx + 117+110 +(num*110)+self.blscroll,mmy-12+109  )
                    ctx.show_text(blend[2][:15])
                
                
                
                
                
                
                
                #### AST BLEND FILE #####
                
                
                
                
                
                # little separator line if scrolled
                
                if (w-(mmx+117+110)) < (len(self.blends)*110+60):
                    widget.window.draw_pixbuf(None, self.fade_02, 0, 0, w-38 , mmy-12, -1, 111, gtk.gdk.RGB_DITHER_NONE, 0, 0)
                
                if self.blscroll < -10:
                    
                    
                    
                    widget.window.draw_pixbuf(None, self.fade_01, 0, 0, mmx+217 , mmy-22, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)
                    
                
                if self.screen.done:
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#5c5c5c"))
                    widget.window.draw_rectangle(xgc, True, mmx , mmy-12,217,110)
                    if mx > mmx + 117 and mx < mmx + 117 + 100 and my > mmy-12 and my < mmy-12 + 100:
                        
                        mouseoverany = True
                        xgc.set_rgb_fg_color(gtk.gdk.color_parse("#db3c16"))
                        widget.window.draw_rectangle(xgc, True, mmx + 117, mmy-12,100,100)
                    
                        xgc.set_rgb_fg_color(gtk.gdk.color_parse("#4c4c4c"))
                    
                        xgc.line_width = 4
                        widget.window.draw_rectangle(xgc, False, mmx + 117, mmy-12,100,100)
                        xgc.line_width = 2
                    
                        # IF CLICKED
                        if "GDK_BUTTON1" in str(fx) and self.allowed and "GDK_BUTTON1" not in str(self.mpf) and win.is_active():
                            
                            os.system("xdg-open "+self.screen.ast[1])
                    
                    
                    widget.window.draw_pixbuf(None, self.screen.ast[0], 0, 0, mmx + 117 , mmy-12, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)
                    
                    # OK ICON
                    widget.window.draw_pixbuf(None, self.okicon, 0, 0, mmx + 117 +85 , mmy-12-5, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)
                    
                    
                    
                else:
                    
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#5c5c5c"))
                    widget.window.draw_rectangle(xgc, True, mmx , mmy-12,217,110)
                    widget.window.draw_pixbuf(None, self.blendfileicon, 0, 0, mmx + 117 , mmy-12, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)
                    widget.window.draw_rectangle(xgc, True, mmx + 117, mmy-12+75,100,25)
                    ctx.set_font_size(10)
                    ctx.move_to(mmx + 117+15, mmy-12+75+15  )
                    ctx.show_text("/ast/ ASSET NOT")
                    ctx.move_to(mmx + 117+15, mmy-12+75+15 + 12 )
                    ctx.show_text("YET FINISHED !!!")
                        
                
                
                        
                        
                    
                    #print blend[2]
                
                
                
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#868686")) ## CHOSE COLOR
                widget.window.draw_rectangle(xgc, True, 0,50, mmx+100, mmy+80) 
                
                ### MAIN MENU  ####
                
                
                
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#aaa"))
                
                widget.window.draw_rectangle(xgc, True, 40, 60, mmx+20, mmy+20)
                widget.window.draw_rectangle(xgc, True, 40, 60, mmx+50, 60)
                widget.window.draw_rectangle(xgc, True, 40, 80+mmy-30, mmx+50, 30)
                
                
                #folder
                
                #mouse over
                if mx in range(mmx+60, mmx+60+22) and my in range(65, 65+22):
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#e47649"))
                    widget.window.draw_rectangle(xgc, True, mmx+60, 65, 22, 22)
                
                    # TOOLTIP
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#aaa"))   
                    widget.window.draw_rectangle(xgc, True, mx+20, my+5, 200, 20)
                    ctx.set_font_size(15)
                    ctx.set_source_rgb(0,0,0)
                    ctx.move_to( mx+30, my+20)
                    ctx.show_text("OPEN ITEM FOLDER")
                    
                    # IF CLICKED
                    if "GDK_BUTTON1" in str(fx) and self.allowed and "GDK_BUTTON1" not in str(self.mpf) and win.is_active():
                        
                        os.system("nautilus "+self.screen.path)
                    
                    
                widget.window.draw_pixbuf(None, self.foldericon, 0, 0, mmx+60, 65, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)
                
                
                
                
                
                
                #checklist
                #mouse over
                if mx in range(mmx+60, mmx+60+22) and my in range(90, 90+22):
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#e47649"))
                    widget.window.draw_rectangle(xgc, True, mmx+60, 90, 22, 22)
                    
                    # TOOLTIP
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#aaa"))   
                    widget.window.draw_rectangle(xgc, True, mx+20, my+5, 200, 20)
                    ctx.set_font_size(15)
                    ctx.set_source_rgb(0,0,0)
                    ctx.move_to( mx+30, my+20)
                    ctx.show_text("ITEM'S CHECKLIST")
                    ctx.set_source_rgb(1,1,1)
                    
                    if "GDK_BUTTON1" in str(fx) and self.allowed and "GDK_BUTTON1" not in str(self.mpf) and win.is_active():
                        
                        checklist.checkwindow(pf=self.pf, title=self.screen.name, FILE=self.screen.path+"/asset.progress")
                    
                    
                widget.window.draw_pixbuf(None, self.checklisticon, 0, 0, mmx+60, 90, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)
                
                
                
                
                # edit preview
                #mouse over
                if mx in range(mmx+60, mmx+60+22) and my in range(80+mmy-27, 80+mmy-27+22):
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#e47649"))
                    widget.window.draw_rectangle(xgc, True, mmx+60, 80+mmy-27, 22, 22)
                    
                    # TOOLTIP
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#aaa"))   
                    widget.window.draw_rectangle(xgc, True, mx+20, my+5, 200, 20)
                    ctx.set_font_size(15)
                    ctx.set_source_rgb(0,0,0)
                    ctx.move_to( mx+30, my+20)
                    ctx.show_text("EDIT PREVIEW")
                    
                    # IF CLICKED
                    if "GDK_BUTTON1" in str(fx) and self.allowed and "GDK_BUTTON1" not in str(self.mpf) and win.is_active():
                        
                        def dobutton(w=None):
                            dialogs.editPreview(self.screen.path, box)
                            self.blends = self.loadBlendFiles(self.screen)
                            self.iteminfo = self.loaditem(self.screen)
                            
                            self.screen.preview = thumbnailer.thumbnail(self.screen.path+"/renders/Preview.jpg", 400, 400)
                            self.screen.preview = gtk.gdk.pixbuf_new_from_file(self.screen.preview)
                            
                            
                            
                            
                        glib.timeout_add(10, dobutton)
                    
                widget.window.draw_pixbuf(None, self.editicon, 0, 0, mmx+60, 80+mmy-27, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)
                
                
                
                # draw preview
                
                
                
                
                
                widget.window.draw_pixbuf(None, self.screen.preview, 0, 0, 50, 70, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)
                
                ## top pannel
                
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#727272")) ## CHOSE COLOR
                widget.window.draw_rectangle(xgc, True, 0, 0, w, 50)
                     
                
                
                
                
                # BIG PERCENTAGE BAR FOR THE ENTIRE CATEGORY
                ctx.set_source_rgb(1,1,1)
                ctx.set_font_size(20)
                ctx.move_to( 20, 30)
                ctx.show_text(str(int(self.screen.percent*100))+" %")
                
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#000")) ## CHOSE COLOR
                widget.window.draw_rectangle(xgc, False, 100, 5, w-110, 40)
                
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#3c3c3c"))
                
                widget.window.draw_rectangle(xgc, True, 102, 7, int((w-114)*self.screen.percent), 36)
                
                ctx.move_to( 150, 30)
                ctx.show_text(self.screen.name)
                
                
                        
                    
                        
            
            if mouseoverany:
                widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))     
            else:  # IF MOUSE NOT IN EDITOR
                widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.ARROW))    
                
                
                
            # TESTING SOMETHING
            ctx.set_font_size(20)
            ctx.move_to( mx, my)
            #ctx.show_text(str(mx)+":"+str(my)+"  "+str(self.winactive)+"   "+str(fx)) 
            
            self.dW = w
            self.DH = h
            
            self.mpx = mx
            self.mpy = my
            self.mpf = fx
            
            
            
            def callback():
                if self.allowed == True:
                    widget.queue_draw()

            glib.timeout_add(10, callback)
            
            
            
            
        graph = gtk.DrawingArea()
        graph.set_size_request(500,700)
        
        
        
        
        
        
        
        
        self.box.pack_start(graph)
        graph.connect("expose-event", framegraph) 
        
        self.box.show_all()        
        
        
    def call_add_dialog(self):
               
        self.newitem = dialogs.AddAsset(self.pf, self.CUR)
        self.newitem = self.newitem.add()
        
        print self.newitem
        
        self.justadded = True
        self.folder_read()
    
    
    
    def loaditem(self, i): 
        
        #### LOADING RENDERS, TEXTURES AND ALL THAT CRAP TO MEMORY
        # as previews and their links
        
        
        
        info = []  #PLACE HOLDER FOR ALL THE ICONS AND STUFF
        
        
        
        ## Renders
        
        
        
        for part in ["renders", "tex", "reference"]:
            
            renders = []
            
            for FILE in os.walk(self.pf+"/dev/"+self.CUR+"/"+i.name+"/"+part).next()[2]:
                
                # getting photos, images
                
                pic = self.pf+"/py_data/icons/pic_big.png"
                pic = gtk.gdk.pixbuf_new_from_file(pic)
                
                for f in fileformats.images:
                    
                    
                    
                    if FILE.endswith(f):
                        
                        #try making a thubnail
                        
                        
                        try:
                            pic = thumbnailer.thumbnail(self.pf+"/dev/"+self.CUR+"/"+i.name+"/"+part+"/"+FILE, 100, 100)
                            pic = gtk.gdk.pixbuf_new_from_file(pic)
                        except:
                            pic = self.pf+"/py_data/icons/pic_big.png"
                            pic = gtk.gdk.pixbuf_new_from_file(pic)
                            
                        renders.append( [pic, self.pf+"/dev/"+self.CUR+"/"+i.name+"/"+part+"/"+FILE, FILE, "IMAGE"] )
                                  
                for f in fileformats.videos:
                    
                    
                    
                    if FILE.endswith(f):
                        
                        #try making a thubnail
                        
                        
                        try:
                            pic = thumbnailer.videothumb(self.pf+"/dev/"+self.CUR+"/"+i.name+"/"+part+"/"+FILE, 100)
                            pic = gtk.gdk.pixbuf_new_from_file(pic)
                        except:
                            pic = self.pf+"/py_data/icons/pic_big.png"
                            pic = gtk.gdk.pixbuf_new_from_file(pic)
                            
                        renders.append( [pic, self.pf+"/dev/"+self.CUR+"/"+i.name+"/"+part+"/"+FILE, FILE, "VIDEO"] )             
            
                # getting videos
            
            
            
            
            info.append(renders)
        
        return info
        
    def loadBlendFiles(self, i):
        
        blends = []
        
        
        for FILE in os.walk(self.pf+"/dev/"+self.CUR+"/"+i.name).next()[2]:
            
            if FILE.endswith(".blend"):
                
                
                try:
                    pic = thumbnailer.blenderthumb(self.pf+"/dev/"+self.CUR+"/"+i.name+"/"+FILE, 100, 100)
                    pic = gtk.gdk.pixbuf_new_from_file(pic)
                    
                except:
                    pic = self.pf+"/py_data/icons/pic_big.png"
                    pic = gtk.gdk.pixbuf_new_from_file(pic)
        
                blends.append( [pic, (self.pf+"/dev/"+self.CUR+"/"+i.name+"/"+FILE), FILE, "BLEND"] )
        
        return blends
        
            
    
    def folder_read(self):
        
        self.assets = []
        
        tmp = []         
        for i in os.walk(self.pf+"/dev/"+self.CUR).next()[1]:
            tmp.append(i)
            
        for i in sorted(tmp):    
            thisasset = asset(self.pf, self.pf+"/dev/"+self.CUR+"/"+i, self.CUR, i)
            print thisasset.info()
            self.assets.append(thisasset)
         
