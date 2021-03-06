# -*- coding: utf-8 -*-

# system
import os
import socket

# graphics interface
import gtk
import pango
import cairo
import glib
import random

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
import render_lists

import copy # OMG OPTIMIZATION HACKS OMG I HOPE IT'S GOING TO WORK

# FIRST LET'S BREAK APPRAT THE DATA STRUCTURE


#   name        color         comment

#   EVENT       #4c4c4c       THE HAPPENING OF SOMETHING REGARDLESS OF IF IT'S SHOWN IN THE MOVIE
#   SCENE       #db3c16       THE ACTUALL SHOWN STUFF ( ON TOP OF THE HAPPENING )
#   CUT         #e47649       THE CONNECTIONS BETWEEN THE SCENES TO KEEP TRACK OF THE MOVIE EDITING



# FILES .bos  #blender organizer story




#### MAIN STORY CLASS TO CALL ALL THE FUNCTIONS FROM

class story:
    
    
    def __init__(self, pf, box, win):
        
        
        self.pf = pf
        self.box = box
        self.win = win
        
        
        self.allowed = True
        
        
        
        self.keys = []
        
        # make a .bos file if no files exits in /pln/
        
        notfound = True
        for FILE in os.walk(self.pf+"/pln").next()[2]:
            if FILE.endswith(".bos"):
                print FILE
                notfound = False
        
        
        if notfound:
            print "Making a missing main.bos"
        
        # LOADING THE FILE
            
            self.FILE = bos(self.pf+"/pln/main.bos")
        else:
            
            if os.path.exists(self.pf+"/pln/main.bos"):
                self.FILE = bos(self.pf+"/pln/main.bos")
            else:
                self.FILE = bos(self.pf+"/pln/"+FILE)
            
        self.FILE.load()
        print self.FILE.filename
        
        
        self.editor()
    
    def events_overlap(self, my, mx, ex, ey, esx, esy, this_frame_events):
        
        overlap = False
        
        for ind, event in enumerate(this_frame_events):
        
            if my in range(event[1], event[1]+event[3]):
            
                for p in range(event[0], event[0]+event[2]):
                    
                    if p in range(ex, ex+esx):
                    
                        
                        overlap = True
                        return event, overlap
        
        
        return None, overlap
        
        
    def editor(self):
    
        # TRANSFORMATION
        self.sx = 1.0
        self.sy = 20.0
        self.px = 0.0
        self.py = 0.0
        
        
        self.select = "bos"
        
        
        self.FILE = bos("pln/main.bos")
        self.px, self.py, self.sx, self.sy = self.FILE.load()
        
        
        
        self.dW = 0
        self.DH = 0
        
        self.mpx = 0
        self.mpy = 0
        self.mpf = None
        
        self.bosscroll = 0    
        
        self.event_text_scroll = 0.0
        
        
        #editor features
        
        # tools:
        # grab, event, scene, cut
        
        
        self.tool = "select"
        # events
        self.toolactive = False
        
        self.toolXY = [0,0]
        
        self.event_resize = False
        self.event_move = False
        self.event_select = False
        
        
        #scenes
        self.scene_select = False
        self.scenes_in_event = []
        
        
        
        #arrows
        self.arrow_to = False
        self.arrow_selection = [False, False]
        self.arrow_delete_overwrite = [[False], [0,0]] ### FOR THE OVERWRITE AUTOMATIC DELETION 
                                                       # [ [ IND OF THE DELETABLE ARROW ],
                                                       # [ COORDINATES FOR THE RENDERER ] ]
        
        self.marker_select = False
        self.deletelastframe = False 
        self.renamelastframe = False
        self.move_marker = False
        
        
        
        
        ### SHOTS HANDELLIGN OMG ####
        
        self.shotsDATA = [] # INSIDE THERE IS A FOLLOWING LIST OF LISTS
                            # [ "SHOT NAME" FALSE if not a shot, 
                            #"SHOT TEXT", 
                            #shotpreview pixbuf FALSE if not loaded; "NONE" if not found ] 
        
        self.shotsSCROLL = 0
        
        
        
        # LOADING ALL THE ICONS
        self.bosicon = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/bos_big.png")
        
        self.eventicon = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/event.png")
        self.scenceicon = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/scene_editor.png")
        self.markericon = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/marker.png")
        self.saveicon = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/big_save.png")
        self.cuticon = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/new_cut.png")
        self.split_event = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/split_event.png")
        self.split_action = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/split_action.png")
        
        #start end
        
        self.start_grey = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/start_grey.png")
        self.start_mo = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/start_mo.png")
        self.start_active = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/start_active.png")
        
        
        
        self.end_grey = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/end_grey.png")
        self.end_mo = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/end_mo.png")
        self.end_active = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/end_active.png")
        
        self.gen_script = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/gen_script.png")
        self.gen_script_active = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/gen_script_active.png")
        
        self.sequence = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/sequence.png")
        
        
        self.render_big = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/render_big.png")
        
        
        
        #shots editor
        self.empty_frame = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/empty_frame.png")
        self.foldericon = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/folder.png")
        self.imgAT = []
        
        
        self.BLboard = ""
        self.copy = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/copy.png")
        self.paste = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/paste.png")
        self.plus = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/plus.png")
        self.render = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/render.png")
        
        
        self.fade_01 = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/INT/fade_01.png")
        self.fade_02 = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/INT/fade_02.png")
        self.fade_03 = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/INT/fade_03.png")
        self.fade_04 = gtk.gdk.pixbuf_new_from_file(self.pf+"/py_data/icons/INT/fade_04.png")
        
        
        
        
        self.scnPERCENT = get_scenes_percentage(self.FILE)
        
        
        
        def framegraph(widget, event):
                                                    
            w, h = widget.window.get_size()
            xgc = widget.window.new_gc()
            
            mx, my, fx  = widget.window.get_pointer()
            tx, ty = self.toolXY
            
            # GETTING WHETHER THE WINDOW IS ACTIVE
            
            self.winactive = self.win.is_active()
            

            
            #######   LINKCHAINED   ######
            
            
            #trying to get whether the start actually connects to end
            linkchained = False
            
            linkchainpath = []
            
            startlink = False
            
            for i in self.FILE.arrows:
                
                if i[0][0] == -1:
                    
                    linkchainpath.append(i)
                    startlink = True
                    
                    
            while startlink: # dangerous motherfucker
                
                found = False
                
                for i in self.FILE.arrows:
                    
                    
                    
                    if linkchainpath[-1][1] == i[0]:
                        
                        
                        
                        found = True
                        linkchainpath.append(i)
                        
                        if i[1][0] == -1:
                            linkchained = True
                            break
                    
                if found == False:
                    break
            
            self.FILE.tree = linkchainpath
            
            ctx = widget.window.cairo_create()
            ctx.select_font_face("Sawasdee", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            
            xgc.line_width = 2
            
            # BACKGROUND COLOR
            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#868686")) ## CHOSE COLOR
            widget.window.draw_rectangle(xgc, True, 0, 0, w, h)  ## FILL FRAME    
            
            
            ctx2 = widget.window.cairo_create()
            ctx2.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            
            
            
            ## tooltips
            
            tooltip = False
            
            
            
            #####################################
            
            
            
            
            
            
            
            
            
            
            
            
            #### EDITOR #######################################################
            
           
            
            
            
            
            
            
            self.arrows_output_dots = []
            
            for i in self.FILE.arrows:
                
                self.arrows_output_dots.append(  [[0,0],[0,0], False]  )
            
            
            
            
            
            # TRANSFORMATION
            sx = self.sx
            sy = self.sy
            px = self.px
            py = self.py
            
            nw = (w-(w)/3)/2
                
            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#999")) ## CHOSE COLOR
            
            xgc.line_width = 1
            widget.window.draw_line(xgc, nw, 0, nw, h) 
            widget.window.draw_line(xgc, 0, h/2, w, h/2) 
            xgc.line_width = 2
            
            
            
            # scroll
            
            if mx > 0 and mx < w-(w)/3 and my > 50:
                # the scroll is done with the middle mouse button
                
                
                ### Y
                if self.mpy > my and "GDK_BUTTON2" in str(fx) and "GDK_BUTTON2" in str(self.mpf) and 65507 not in self.keys and self.win.is_active():
                    
                    self.py = self.py + (my-self.mpy) 
                
                if self.mpy < my and "GDK_BUTTON2" in str(fx) and "GDK_BUTTON2" in str(self.mpf) and 65507 not in self.keys and self.win.is_active():
                    
                    self.py = self.py - (self.mpy-my)
                
                
                
                
                
                ### X
                if self.mpx > mx and "GDK_BUTTON2" in str(fx) and "GDK_BUTTON2" in str(self.mpf) and 65507 not in self.keys and self.win.is_active():
                    
                    self.px = self.px + (mx-self.mpx) 
                
                if self.mpx < mx and "GDK_BUTTON2" in str(fx) and "GDK_BUTTON2" in str(self.mpf) and 65507 not in self.keys and self.win.is_active():
                    
                    self.px = self.px - (self.mpx-mx)
            
                
                
                
                
                
                
                #### RESIZE
                
                if 65451 in self.keys: # + key
                    
                    self.sy = self.sy + 0.3
                    self.sx = self.sx + 0.01
                    
                    
                    
                if 65453 in self.keys: # - key
                    
                    self.sy = self.sy - 0.3
                    self.sx = self.sx - 0.01
                self.arrow_delete_overwrite
                
                
                
                ### Y
                if self.mpy > my and "GDK_BUTTON2" in str(fx) and "GDK_BUTTON2" in str(self.mpf) and 65507 in self.keys and self.win.is_active():
                    
                    self.sy = self.sy - 0.5
                
                if self.mpy < my and "GDK_BUTTON2" in str(fx) and "GDK_BUTTON2" in str(self.mpf) and 65507 in self.keys and self.win.is_active():
                    
                    self.sy = self.sy + 0.5
                
                if self.sy < 5:
                    self.sy = 5
                
                
                
                  
                xsize = 0.03*sx
                
                
                ### X
                if self.mpx > mx and "GDK_BUTTON2" in str(fx) and "GDK_BUTTON2" in str(self.mpf) and 65507 in self.keys and self.win.is_active():
                    
                    
                    
                    
                    self.sx = self.sx - xsize
                    
                    
                    
                if self.mpx < mx and "GDK_BUTTON2" in str(fx) and "GDK_BUTTON2" in str(self.mpf) and 65507 in self.keys and self.win.is_active():
                    
                    self.sx = self.sx + xsize
                    
                
                
                
                
                if self.sx < 0.01:
                    self.sx = 0.01
                
                
                if self.sx != sx or self.sy != sy:
                
                    self.py = (self.py-h/2) / sy * self.sy   + h/2    
                    self.px = (self.px-nw) / sx * self.sx   + nw
                
                
                
                
                
            
            # for sake of it
            # SHORT CUT TO MAKE VIEW NORMILIZE TO STAR UP VALUES
            if 65307 in self.keys:  # ESCAPE BUTTON
                
                self.sx = 1
                self.sy = 20
                self.px = 0
                self.py = 0
            
            
                
                
                
            ## SHOWING MARKERS
            
            allowdelete = False
            if not self.deletelastframe:
                allowdelete = True
                
            allowrename = False
            if not self.renamelastframe:
                allowrename = True
                
            for ind, i in enumerate(self.FILE.markers):
                
                markX = int(i[0]*sx+px)
                textPX = len(i[1])*6  + 2
                
                xgc.line_width = 1
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#00F"))
                
                if self.marker_select == ind:  ## IF MARKER SELECTED
                    
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#66F"))
                    
                    
                    if 65535 in self.keys: # DELETE BUTTON
                        
                        
                        if allowdelete:
                            del self.FILE.markers[ind]
                            self.marker_select = len(self.FILE.markers)+2
                        allowdelete = False
                        self.deletelastframe = True
                    
                    else:
                        self.deletelastframe = False 
                    
                    
                    
                    if 65289 in self.keys:
                        if allowrename:
                            def ee(e=None):
                                dialogs.marker(self.marker_select, self.FILE)
                        
                    
                            glib.timeout_add(10, ee)
                        allowrename = False
                        self.renamelastframe = True
                    else:
                        
                        self.renamelastframe = False
                         
                        
                
                if mx in range(markX-textPX/2, markX+textPX/2) and my in range(h-10, h):    # IF MOUSE OVER
                    
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#66F"))
                    
                        
                    if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active() and self.tool == "select":
                        
                        # IF CLICKED
                        self.marker_select = ind
                        self.event_select = len(self.FILE.events)+2
                        
                        
                        
                
                
                widget.window.draw_line(xgc, markX, 0, markX, h)
                xgc.line_width = 2
                
                
                
                
                widget.window.draw_rectangle(xgc, True, markX-textPX/2, h-10, textPX,10)
                
                
                
                
                ctx2.set_source_rgb(1,1,1)
                ctx2.set_font_size(10)
                ctx2.move_to( markX-textPX/2+1, h-1)
                ctx2.show_text(i[1])
            
            
            if self.tool == "split":
                if "GDK_BUTTON3" not in str(fx) and "GDK_BUTTON3" in str(self.mpf):
                    
                    self.tool = "select"
                
            
            # MOVING MARKERES    
            
            if self.tool == "select":
            
                for ind, i in enumerate(self.FILE.markers):
                    
                    
                    markX = int(i[0]*sx+px)
                    textPX = len(i[1])*6  + 2
                    
                    if self.marker_select == ind:
                        
                        # ACTIVATE MOVE
                        
                        if mx in range(markX-textPX/2, markX+textPX/2) and my in range(h-10, h):    # IF MOUSE OVER
                            if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active():
                                self.move_marker = True
                                self.tool = "select"
                        
                        # MOVING 
                        
                        if self.move_marker and "GDK_BUTTON1" in str(fx):
                
                            self.FILE.markers[self.marker_select][0] = (mx - px)/sx     
                        
                        
                        # STOP THE MOVE
                        
                        
                        if "GDK_BUTTON1" not in str(fx) and "GDK_BUTTON1" in str(self.mpf):
                            
                            
                            self.move_marker = False
                
            
            ################# EVENT TOOL ##################
            
            
            ### SHOWING EVENTS
            
            this_frame_events = []
            self.arrow_to = False
            
            
            start_active = False
            end_active = False
            
            
            for ind, event in enumerate(self.FILE.events):
                
                
                ex = int(event[0] * sx + px)
                ey = int(int(event[2]) * sy + py)
                esx = int(event[1] * sx )
                esy = int(sy)
                
                name = event[3]
                story = event[4]
                
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#4c4c4c"))
                widget.window.draw_rectangle(xgc, True, ex, ey, esx, int(esy))
                
                
                
                
                ############## SHOWING THE SCENES IN THE EVENT #############
                if self.event_select == ind:
                    self.scenes_in_event = []
                
                
                
                if "<scene>" in story and "</scene>" in story:
                    
                    sa = story.count("<scene>") # COUNT AMOUNT OF SCENES
                    
                    ts = story
                    
                    dot = 0
                    dots = []
                    
                    # getting the values of the dots
                    for n in range(sa):
                        
                        dot = dot + ts.find("<scene>")
                        d = [dot]
                        
                        ts = ts[ts.find("<scene>"):]
                        dot = dot + ts.find("</scene>")+8
                        
                        
                        # Adding scenes to a list to process later
                        
                        scene_text = ts[7:ts.find("</scene>")]
                        if self.event_select == ind:
                            self.scenes_in_event.append(scene_text)
                        
                        ts = ts[ts.find("</scene>")+8:]
                        
                        d.append(dot)
                        dots.append(d)
                        
                        
                            
                        
                        
                        
                        
                        
                    
                    
                    # printing them onto the screen
                    
                    for n, i in enumerate(dots):
                        
                        d1, d2 = i
                        
                        
                        
                        ds = int(  ex + ( float(esx) / len(story) *  d1 )  )
                        dw = int(   (float(esx) / len(story) *  d2)-( float(esx) / len(story) *  d1 ))
                        
    
                        xgc.set_rgb_fg_color(gtk.gdk.color_parse("#db3c16"))
                        widget.window.draw_rectangle(xgc, True, ds, ey+3, dw, int(esy)-5)
                        
                        xgc.set_rgb_fg_color(gtk.gdk.color_parse("#4c4c4c"))
                        widget.window.draw_rectangle(xgc, False, ds, ey+3, dw, int(esy)-5)
                        
                        
                        
                        # MAKING SURE WE DRAW THE FUCKING ARROWS TO THE SCREEN LOL
                        
                        scnDATA = self.FILE.get_scenes_data()
                        
                        for arrowN, arrow in enumerate(self.FILE.arrows):
                            
                            
                            # start end arrows
                            if arrow[0][0] == -1:
                                self.arrows_output_dots[arrowN][0] = [30,80]
                                
                                start_active = True
                                
                            if arrow[1][0] == -1:
                                self.arrows_output_dots[arrowN][1] = [w-(w)/3-30,80]
                                
                                end_active = True
                            
                            
                            if arrow in linkchainpath:
                                self.arrows_output_dots[arrowN][2] = True
                                
                            
                            
                            try:
                                if arrow[0][0] == ind:
                                    
                                    if scnDATA[ind][n][1] == arrow[0][1]:
                                    
                                        
                                        self.arrows_output_dots[arrowN][0] = [dw+ds, (ey+(ey+esy))/2]
                                if arrow[1][0] == ind:
                                    
                                    if scnDATA[ind][n][1] == arrow[1][1]:
                                    
                                        
                                        self.arrows_output_dots[arrowN][1] = [ds, (ey+(ey+esy))/2]            
                                        
                                        
                            except:
                                pass        
                            
                            
                            
                        
                        
                        
                        
                        
                        if mx in range(ds, dw+ds) and my in range(ey, int(esy)+ey):
                            
                            
                            tooltip = "event ["+name+"]\nscene["+scnDATA[ind][n][1]+"]"
                            
                            
                            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#FFF"))
                            
                            if self.tool == "arrow":
                                
                                scnDATA = self.FILE.get_scenes_data()
                                
                                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#000"))
                                
                                self.arrow_to = [ds, (ey+(ey+esy))/2]
                                
                                self.arrow_selection[1] = [ind, scnDATA[ind][n][1]]
                                
                            widget.window.draw_rectangle(xgc, False, ds, ey+3, dw, int(esy)-5)
                            
                            
                            if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active() and self.tool == "select": # IF CLICKED
                            
                                self.imgAT = []     
                                self.scene_select = n
                                
                                
                                try:
                                    scnDATA = self.FILE.get_scenes_data()
                                    scenestory = scnDATA[ind][n][3]
                                    
                                    
                                    
                                    self.shotsDATA = get_shots(scenestory, scnDATA[ind][n][1])
                                except:
                                    
                                    
                                    
                                    print "scene loading error"
                                self.shotsSCROLL = 0
                        
                        
                        
                        
                            ## IF TOOL IS SPLIT
                            
                            if self.tool == "split":
                                
                                
                                xgc.line_width = 4
                                
                                
                                END = False # Determents whether we looking at the end of the scene strip or the begining
                                
                                
                                if mx > ds+dw/2:
                                    
                                    END = True
                                    PIXEL = ((ds+dw) -   px)/sx -1
                                    
                                    
                                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#000"))
                                    widget.window.draw_line(xgc, ds+dw, int(esy/2)+ey-50, ds+dw, int(esy/2)+ey+50)
                                    widget.window.draw_pixbuf(None, self.split_action, 0, 0, ds+dw-20-1, int(esy/2)+ey-20 , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
                                else:
                                    
                                    PIXEL = ((ds) -   px)/sx -1
                                    
                                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#000"))
                                    widget.window.draw_line(xgc, ds, int(esy/2)+ey-50, ds, int(esy/2)+ey+50)
                                    widget.window.draw_pixbuf(None, self.split_action, 0, 0, ds-20-1, int(esy/2)+ey-20 , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
                        
                                if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active(): # IF CLICKED
                                
                                
                                    self.FILE.split(ind, i, END, PIXEL, n)
                                    self.tool = "select"
                                
                                xgc.line_width = 2
                                
                        ## IF ARROWS DRAWING
                            
                        if self.toolXY[0] in range(ds, dw+ds) and self.toolXY[1] in range(ey, int(esy)+ey) and self.tool == "arrow":    
                            
                            if self.tool == "arrow":
                                
                                scnDATA = self.FILE.get_scenes_data()
                                
                                self.toolXY = [dw+ds, (ey+(ey+esy))/2]
                                self.arrow_selection[0] = [ind, scnDATA[ind][n][1]]
                                
                                
                                
                                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#000"))
                                widget.window.draw_rectangle(xgc, False, ds, ey+3, dw, int(esy)-5)        
                                
                                
                        if n == self.scene_select and self.event_select == ind and self.tool != "arrow":
                            
                            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#FFF"))
                            
                            widget.window.draw_rectangle(xgc, False, ds, ey+3, dw, int(esy)-5)
                            
                
                
                
                
                
                
                # IF THIS EVEN IS CURRENTLY SELECTED
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#868686"))
                if self.event_select == ind:
                    
                    
                    # TAB
                    
                    
                    
                    if 65289 in self.keys and self.win.is_active():
                        if 65289 in self.keys:
                            self.keys.remove(65289)
                        
                        def ee(e=None):
                            editevent = dialogs.event(name, story, self.FILE, self.event_select)
                            editevent.edit()
                    
                        glib.timeout_add(10, ee)
                    
                    
                    
                    
                    # GUIDING LINES
                    xgc.line_width = 1
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#999"))
                    widget.window.draw_rectangle(xgc, False, 0, ey, w, esy)
                    widget.window.draw_rectangle(xgc, False, ex, -2 , esx, h+2)
                    
                    # select color
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#e47649"))
                    
                widget.window.draw_rectangle(xgc, False, ex, ey, esx, int(esy))
                ctx.set_source_rgb(1,1,1)
                ctx.set_font_size(10)
                ctx.move_to( ex+2, ey+10)
                ctx.show_text(event[3])
                
                
                this_frame_events.append([ex, ey, esx, esy, event[3]])
            
            
            
            
            ###### OUTPUTTING ARROWS TO THE SCREEEEENNNNNN
            
            for dot in self.arrows_output_dots:
                    
                
                
                arx, ary = dot[0]
                tox, toy = dot[1]
                shine    = dot[2]   
                
                if shine:
                    
                    
                    if linkchained:
                        xgc.set_rgb_fg_color(gtk.gdk.color_parse("#FFF"))        
                    else:
                        xgc.set_rgb_fg_color(gtk.gdk.color_parse("#0024ff"))    
                else:
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#000"))
                xgc.line_width = 4
                widget.window.draw_line(xgc, arx, ary, tox, toy)
                xgc.line_width = 1
                
                #TRIANGLES LOL
                dots = (arx-10, ary+10), (arx, ary), (arx-10, ary-10)
                widget.window.draw_polygon(xgc, True, dots)
                
                dots = (tox, toy+10), (tox+10, toy), (tox, toy-10)
                widget.window.draw_polygon(xgc, True, dots)
                
                
                
                
                
            
            # MOUSE CURSOR MAIN
            if mx > 0 and mx < w-(w)/3 and my > 50:
                widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.CROSS))
                
            else:  # IF MOUSE NOT IN EDITOR
                widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.ARROW)) 
            
            
            
            
            
            
            
            ### EDITING EVENTS
            
            if self.tool == "select":
                
                for ind, event in enumerate(this_frame_events):
                    
                    ex = event[0]
                    ey = event[1]
                    esx = int(event[2])
                    esy = int(sy)
                    name = event[4]
                    
                    if mx > 0 and mx < w-(w)/3 and my > 50:
                        # if on the right side TO RESIZE
                        if mx in range(ex-2, ex+2) and my in range(ey, ey+esy):
                            widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.SB_H_DOUBLE_ARROW))
                            if "GDK_BUTTON1" in str(fx) and self.allowed and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active():
                                self.event_resize = [0, ind]  
                                self.event_select = ind
                                self.marker_select = len(self.FILE.markers)+2
                        # if on the left side TO RESIZE
                        elif mx in range(ex+esx-2, ex+esx+2) and my in range(ey, ey+esy):
                            widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.SB_H_DOUBLE_ARROW))
                            if "GDK_BUTTON1" in str(fx) and self.allowed and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active():
                                self.event_resize = [1, ind]  
                                self.event_select = ind
                                self.marker_select = len(self.FILE.markers)+2
                        
                        # selecting or moving the thingy
                        elif mx in range(ex, ex+esx) and my in range(ey, ey+esy):
                            
                           # get mouse to show the grabber
                            widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.FLEUR))
                            
                            # show the selection color around
                            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#e47649"))
                            widget.window.draw_rectangle(xgc, False, ex, ey, esx, esy)
                            
                            
                            if "GDK_BUTTON1" in str(fx) and self.allowed and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active():
                                
                                self.event_move = [True, ind]
                                self.event_select = ind
                                self.marker_select = len(self.FILE.markers)+2
                    
                            
            ###### MOVING EVENTS    #####
            
            
            if self.event_move:
                
                ind = self.event_move[1]
                
                
                
                #### X
                if self.mpx > mx and "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" in str(self.mpf):
                        
                    self.FILE.events[ind][0] = self.FILE.events[ind][0] + (mx-self.mpx ) / sx
                    
                    
                if self.mpx < mx and "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" in str(self.mpf):
                    
                    self.FILE.events[ind][0] = self.FILE.events[ind][0] - (self.mpx-mx  ) / sx
                
                
                ### Y
                
                if self.mpy > my and "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" in str(self.mpf):
                        
                    self.FILE.events[ind][2] = self.FILE.events[ind][2] + float(my-self.mpy ) / sy 
                    
                    
                if self.mpy < my and "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" in str(self.mpf):
                    
                    self.FILE.events[ind][2] = self.FILE.events[ind][2] - float(self.mpy-my  ) / sy 
                
                
                    
                if "GDK_BUTTON1" not in str(fx) and "GDK_BUTTON1" not in str(self.mpf):
                    
                    # SO FAR THE BUG IS MADE BY THE DELETING OF EVENT WTF
                    try:
                        self.FILE.events[ind][2] = int(self.FILE.events[ind][2])
                        self.event_move = False
                    except:
                        pass
                
                
            
            #### RESIZING EVENTS #######
            
            if self.event_resize:
                
                direction = self.event_resize[0]
                ind = self.event_resize[1]
                
                if direction == 0:
                    if self.mpx > mx and "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" in str(self.mpf):
                        
                        self.FILE.events[ind][0] = self.FILE.events[ind][0] + (mx-self.mpx ) / sx
                        self.FILE.events[ind][1] = self.FILE.events[ind][1] - (mx-self.mpx ) / sx
                    
                    if self.mpx < mx and "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" in str(self.mpf):
                        
                        self.FILE.events[ind][0] = self.FILE.events[ind][0] - (self.mpx-mx  ) / sx
                        self.FILE.events[ind][1] = self.FILE.events[ind][1] + (self.mpx-mx  ) / sx
                    
                    if self.FILE.events[ind][1] < 2:
                        
                        self.event_resize = [1, ind]
                    
                if direction == 1:
                    if self.mpx > mx and "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" in str(self.mpf):
                        
                        self.FILE.events[ind][1] = self.FILE.events[ind][1] + (mx-self.mpx ) / sx
                        
                    
                    if self.mpx < mx and "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" in str(self.mpf):
                        
                        self.FILE.events[ind][1] = self.FILE.events[ind][1] - (self.mpx-mx  ) / sx
                        
                    
                    if self.FILE.events[ind][1] < 2:
                        
                        self.event_resize = [0, ind]
                
                
                
                
                
                
                
                
                if "GDK_BUTTON1" not in str(fx) and "GDK_BUTTON1" not in str(self.mpf):
                    
                    self.event_resize = False
                
                
                
                
                    
                    
            
            
            if self.tool == "event":
                
                
                if "GDK_BUTTON3" in str(fx): ## CANCEL with right mouse button
                    
                    self.tool = "select"
                    self.toolactive = False
                
                
                
                # Activate
                
                if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active():
                    
                    
                    if mx > 0 and mx < w-(w)/3 and my > 50:
                    
                        # saving the xy for the event
                        self.toolXY = [mx, my]
                        
                        widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.SB_H_DOUBLE_ARROW))
                        
                        self.toolactive = True
                # Active
                if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" in str(self.mpf) and self.toolactive:
                    
                    widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.SB_H_DOUBLE_ARROW))
                    
                    if tx < mx:
                        pureX = (tx -   px)/sx  - 1
                        pureS = (mx-tx)/sx
                    else:
                        pureX = (mx  -  px)/sx  - 1
                        pureS = (tx-mx)/sx
                    pureY = (my    - py   )/sy
                        
                    
                    ex = int(pureX * sx + px)
                    ey = int(pureY * sy + py)
                    esx = int(pureS * sx )
                    esy = int(sy)
                    
                        
                        
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#5c5c5c"))
                    
                    
                    # IF OVERLAPS WITH ANOTHER ONE
                    event, overlap = self.events_overlap(my, mx, ex, ey, esx, esy, this_frame_events)
                        
                        
                        
                        
                        
                        
                    if overlap:    
                        xgc.set_rgb_fg_color(gtk.gdk.color_parse("#F00"))
                        
                        widget.window.draw_rectangle(xgc, False, event[0], event[1], event[2], event[3])
                            
                            
                            
                    widget.window.draw_rectangle(xgc, False, ex, ey, esx, esy)
                    
                
                
                # Release
            
                if "GDK_BUTTON1" not in str(fx) and "GDK_BUTTON1" in str(self.mpf) and self.toolactive:
                    
                    
                    
                    
                    
                    
                    
                    # making the math of the values before saving 
                    
                    
                    
                        
                    if tx < mx:
                        pureX = (tx -   px)/sx  - 1
                        pureS = (mx-tx)/sx
                    else:
                        pureX = (mx  -  px)/sx  - 1
                        pureS = (tx-mx)/sx
                    pureY = (my    - py   )/sy
                    
                    
                    
                    
                    
                    eventname = "Event"
                    storypart = "Something is happening."
                    foundtimes = 0
                    for event in self.FILE.events:
                        if event[3].startswith(eventname):
                            foundtimes = foundtimes + 1
                    
                    if foundtimes > 0:
                        eventname = eventname + "_" + str(foundtimes+1)
                        
                    
                    # getting the event editor
                    
                    def ee(e=None):
                        editevent = dialogs.event(eventname, storypart, self.FILE, len(self.FILE.events)-1)
                        editevent.edit()
                    
                    glib.timeout_add(10, ee)
                    
                    self.FILE.events.append([pureX, pureS, pureY, eventname, storypart])
                    self.event_select = len(self.FILE.events)-1
                    
                    self.tool = "select"
                    self.toolactive = False
                    
                    self.marker_select = len(self.FILE.markers)+2
            
            
            # ARROW DRAW
            
            
            if self.tool == "arrow":
                
                if "GDK_BUTTON3" in str(fx): ## CANCEL with right mouse button
                    
                    self.tool = "select"
                    self.toolactive = False
                        
                # Activate
                
                if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active():
                    
                    
                    if mx > 0 and mx < w-(w)/3 and my > 50:
                    
                        # saving the xy for the event
                        self.toolXY = [mx, my]
                        
                        widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.DOT))
                        
                        self.toolactive = True
                
                
                
                # Active
                if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" in str(self.mpf) and self.toolactive:
                    
                    
                    tx, ty = self.toolXY
                    
                    xgc.line_width = 4
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#000"))
                    if self.arrow_selection in self.FILE.arrows:
                        xgc.set_rgb_fg_color(gtk.gdk.color_parse("#888"))
                        
                    
                    
                    #FIRST TRIANGLE
                    dots = (tx-10, ty+10), (tx, ty), (tx-10, ty-10)
                    widget.window.draw_polygon(xgc, True, dots)
                    
                    if self.arrow_to == False:
                        widget.window.draw_line(xgc, tx, ty, mx, my)
                        
                        
                        
                        
                        
                        dots = (mx, my+10), (mx+10, my), (mx, my-10)
                        widget.window.draw_polygon(xgc, True, dots)
                    
                    else:
                        widget.window.draw_line(xgc, tx, ty, self.arrow_to[0], self.arrow_to[1])
                        
                        
                        dots = (self.arrow_to[0], self.arrow_to[1]+10), (self.arrow_to[0]+10, self.arrow_to[1]), (self.arrow_to[0], self.arrow_to[1]-10)
                        widget.window.draw_polygon(xgc, True, dots)
                    
                    
                    # Release
            
                if "GDK_BUTTON1" not in str(fx) and "GDK_BUTTON1" in str(self.mpf) and self.toolactive:
                    
                    
                    
                    
                    if False not in self.arrow_selection and self.arrow_selection[0] != self.arrow_selection[1]:
                        if self.arrow_selection not in self.FILE.arrows:
                            self.FILE.arrows.append(self.arrow_selection)
                        else:
                            self.FILE.arrows.remove(self.arrow_selection)    
                            
                            
                
            
                    self.arrow_selection = [False, False]
                    
                    self.FILE.clear_arrows()
                
                    self.marker_select = len(self.FILE.markers)+2
                
            
            # ADD MARKER
            
            if self.tool == "marker":
                
                if "GDK_BUTTON3" in str(fx): ## CANCEL with right mouse button
                    
                    self.tool = "select"
                    self.toolactive = False
            
                xgc.line_width = 1
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#00F"))
                widget.window.draw_line(xgc, mx, 0, mx, h)
                xgc.line_width = 2
            
            
            
            #  CLICK
                
                if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) :
                    
                    
                    self.FILE.markers.append( [ (mx - px)/sx , "MARK" ] )
                    
                    
                    def ee(e=None):
                        dialogs.marker(len(self.FILE.markers)-1, self.FILE)
                        
                    
                    glib.timeout_add(10, ee)
                        
                        
                    self.marker_select = len(self.FILE.markers)-1
                    
                    
                    self.tool = "select"
                    self.toolactive = False
            
            ### TOP N SIDE PANEL
                
                
            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#5c5c5c"))
            widget.window.draw_rectangle(xgc, True, 0, 0, w-(w)/3, 50) 
            
                
            
            
            
            
            ################################### TOP PANEL ICONS
            
            #SAVE BUTTON
            
            saveshortcut = False
            if 65507 in self.keys and 115 in self.keys:
                saveshortcut = True
            if 65507 in self.keys and 83 in self.keys:
                saveshortcut = True
            
            if mx in range(360+50,400+50) and my in range(5,45):
                
                
                tooltip = "[ CTRL - S ]\n\nSave File to \n/pln/main.bos"
                
                
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#999"))
                widget.window.draw_rectangle(xgc, True, 260+100+50, 5, 40, 40)
                
                if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active() :
                    
                    saveshortcut = True
            
            if saveshortcut:
                
                
                
                widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
                
                while gtk.events_pending():
                    gtk.main_iteration()
                   
                self.FILE.save(px,py,sx,sy)
            
            widget.window.draw_pixbuf(None, self.saveicon, 0, 0, 160+150+50+50, 5 , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0) 
            
            
            # EVENT BUTTON
            
            
            if 69 in self.keys or 101 in self.keys:   # SHORT CUT
                self.tool = "event"                   # PRESS E
                self.toolactive = False
            
            if self.tool == "event":
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#e47649"))
                widget.window.draw_rectangle(xgc, True, 160, 5, 40, 40)
            else:
                if mx in range(160, 200) and my in range(5,45):
                    
                    tooltip = "[ E ]\n\nAdd Event\nA part of scrip/story\nin relation to time"
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#999"))
                    widget.window.draw_rectangle(xgc, True, 160, 5, 40, 40)
                    
                    if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active():
                        
                        self.tool = "event"
                        self.toolactive = False
            
            widget.window.draw_pixbuf(None, self.eventicon, 0, 0, 160, 5 , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0) 
            
            
            
            # ADD SCENE BUTTON
            addscenenowshortcut = False
            if 83 in self.keys and self.win.is_active() and 65507 not in self.keys and not saveshortcut:
                if 83 in self.keys:
                    self.keys.remove(83)
                addscenenowshortcut = True
            if 115 in self.keys and self.win.is_active() and 65507 not in self.keys and not saveshortcut:
                
                if 115 in self.keys:
                    self.keys.remove(115)
                addscenenowshortcut = True
                
                
            
            if mx in range(210,240) and my in range(5,45):
                
                tooltip = "[ S ]\n\nSelect a scene\nwithin an event"
                
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#999"))
                widget.window.draw_rectangle(xgc, True, 210, 5, 40, 40)
                
                if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active() and len(self.FILE.events):
                    addscenenowshortcut = True
            if addscenenowshortcut and len(self.FILE.events):
                    
                self.tool = "select"
                self.toolactive = False
                
                event = self.FILE.events[self.event_select]
            
                name = event[3]
                story = event[4]
                
                def justdoit(v=None):
                    sae = dialogs.event(name, story, self.FILE, self.event_select)
                    sae.add_scene()
                glib.timeout_add(10, justdoit)
                    
            
            
             
            widget.window.draw_pixbuf(None, self.scenceicon, 0, 0, 160+50, 5 , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
            
            
            
            
            # ADD CONNECTION BUTTON
            
            if 97 in self.keys or 65 in self.keys:   # SHORT CUT
                self.tool = "arrow"                   # PRESS E
                self.toolactive = False
            
            
            if self.tool == "arrow":
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#e47649"))
                widget.window.draw_rectangle(xgc, True, 260, 5, 40, 40)
            else:
                if mx in range(260,290) and my in range(5,45):
                    
                    tooltip = "[ A ]\n\nArrow connection\nto guide editing of the scenes"
                    
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#999"))
                    widget.window.draw_rectangle(xgc, True, 260, 5, 40, 40)
                    
                    if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active() and len(self.FILE.events):
                        
                        self.tool = "arrow"
                        self.toolactive = False
            
            widget.window.draw_pixbuf(None, self.cuticon, 0, 0, 160+100, 5 , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
            
            
            # SPLIT EVENT BETWEEN SCENES
            
            
            if 75 in self.keys or 107 in self.keys:
                
                
                self.tool = "split"                   # PRESS K
                self.toolactive = False
            
            
            if self.tool == "split":
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#e47649"))
                widget.window.draw_rectangle(xgc, True, 260+50, 5, 40, 40)
            else:
                if mx in range(310,340) and my in range(5,45):
                
                
                    tooltip = "[ K ]\n\nSplit events between the scenes\nlike a Knife"
                        
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#999"))
                    widget.window.draw_rectangle(xgc, True, 260+50, 5, 40, 40)
                    
                    if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active() :
                        
                        self.tool = "split"
                        self.toolactive = False
                    
                    
            widget.window.draw_pixbuf(None, self.split_event, 0, 0, 160+150, 5 , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
            
            
            
            # ADD MARKER
            
            if 77 in self.keys or 109 in self.keys:
                
                
                self.tool = "marker"                   # PRESS M
                self.toolactive = False
            
            
            if self.tool == "marker":
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#e47649"))
                widget.window.draw_rectangle(xgc, True, 260+50+50, 5, 40, 40)
            else:
                if mx in range(310+50,340+50) and my in range(5,45):
                    
                    tooltip = "[ M ]\n\nMark an important timepoint"
                    
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#999"))
                    widget.window.draw_rectangle(xgc, True, 260+50+50, 5, 40, 40)
                    
                    if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active() :
                        
                        self.tool = "marker"
                        self.toolactive = False
            
            
            
            
            
            
            
            
            
            
            
            widget.window.draw_pixbuf(None, self.markericon, 0, 0, 160+150+50, 5 , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
            
            
            
            
            
            ##############   >>>>     SCENE PERSENTAGE <<<<<<   #################
            
            
            
            
            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#8c8c8c"))
            widget.window.draw_rectangle(xgc, False, 260+150+50, 5, w-(w)/3-110-(260+150+100), 40)
            
            
            widget.window.draw_rectangle(xgc, True, 260+150+50, 5, int((w-(w)/3-110-(260+150+100))*self.scnPERCENT), 40)
            
            ctx.set_source_rgb(1,1,1)
            ctx.set_font_size(15)
            ctx.move_to( 260+150+50, 20)
            ctx.show_text(str(int(self.scnPERCENT*100))+"%")
            
            
            
            
            
            if "GDK_BUTTON1" not in str(fx) and "GDK_BUTTON1" in str(self.mpf) and self.win.is_active() : # IF RELEASED
            
                self.scnPERCENT = get_scenes_percentage(self.FILE)
            
            
            
            
            
            
                
            ### RENDER LISTS BUTTON ###
            
            
            if mx in range(w-(w)/3-150, w-(w)/3-110) and my in range(5, 45):
            
            
                
                tooltip = "Manage Render Lists\n\nCreate Lists to render\nmore then 1 blend file\nat ones in a sequence."
            
                if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active() : # IF CLICKED
                
                    def ee(e=None):
                        render_lists.main(self.pf)
                    
                    glib.timeout_add(10, ee)
                
                
                
                    
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#999"))
                widget.window.draw_rectangle(xgc, True, w-(w)/3-150, 5, 40, 40)
            
            
            
            
            
                
            widget.window.draw_pixbuf(None, self.render_big, 0, 0, w-(w)/3-150, 5 , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
            
                
                
                
                
                
                
                
            #########   START >>>>>>>>>>> END ##########
            
            
            
            
            
            
            
            ### VIEW SCRIPT BUTTON ###
            
            
            if mx in range(w-(w)/3-50, w-(w)/3-10) and my in range(5, 45):
            
            
                if linkchained:
                    tooltip = "View Full Script"
                
                    if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active() : # IF CLICKED
                    
                        def ee(e=None):
                            editevent = dialogs.event(False, False, self.FILE, len(self.FILE.events)-1)
                            editevent.view_script(linkchainpath)
                        
                        glib.timeout_add(10, ee)
                
                
                else:
                    tooltip = "Connect arrows [ A ]\nfrom Start to End circles\nthrough all the movie scenes\nif this icon will glow\nyou will be able to\nview full script"
                    
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#999"))
                widget.window.draw_rectangle(xgc, True, w-(w)/3-50, 5, 40, 40)
            
            
            
            
            if linkchained:
                
                widget.window.draw_pixbuf(None, self.gen_script_active, 0, 0, w-(w)/3-50, 5 , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
            else:
                
                widget.window.draw_pixbuf(None, self.gen_script, 0, 0, w-(w)/3-50, 5 , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
            
            
            
            
            
            #start
            if mx in range(10, 50) and my in range(60, 110):
                tooltip = "Start of the film\n\n Connect to the first scene\nwith the arrow tool [ A ]"
                widget.window.draw_pixbuf(None, self.start_mo, 0, 0, 10, 60 , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
            else:
                
                if start_active:
                    widget.window.draw_pixbuf(None, self.start_active, 0, 0, 10, 60 , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)                  
                else:
                    widget.window.draw_pixbuf(None, self.start_grey, 0, 0, 10, 60 , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
            
            if tx in range(10, 50) and ty in range(60, 110):    
                if self.tool == "arrow" and "GDK_BUTTON1" in str(fx):
                
                    self.arrow_selection[0] = [-1,"start"]
                
                
                
            
            
            
            
            
            #end
            if mx in range(w-(w)/3-50, w-(w)/3-10) and my in range(60, 110):
                tooltip = "End of the film\n\n Connet the ending scene to it\nwith the arrow tool [ A ]"
                widget.window.draw_pixbuf(None, self.end_mo, 0, 0, w-(w)/3-50, 60 , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
                
                
                if self.tool == "arrow" and "GDK_BUTTON1" in str(fx):
                
                    self.arrow_selection[1] = [-1,"end"]
                
            else:
                if end_active:
                    widget.window.draw_pixbuf(None, self.end_active, 0, 0, w-(w)/3-50, 60 , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
                else:
                    widget.window.draw_pixbuf(None, self.end_grey, 0, 0, w-(w)/3-50, 60 , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
            
            
            
            
            
            
            
            #### SEQUENCE EDITOR REACH BUTTON #####
            
            if mx in range(w-(w)/3-100, w-(w)/3-60) and my in range(5, 45):
            
            
                
                tooltip = "Edit Movie\n Open /rnd/sequence.blend"
            
                if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active() : # IF CLICKED
                
                    os.system("xdg-open "+self.pf+"/rnd/sequence.blend")
                
                
                
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#999"))
                widget.window.draw_rectangle(xgc, True, w-(w)/3-100, 5, 40, 40)
            
            
            
            
            
                
            widget.window.draw_pixbuf(None, self.sequence, 0, 0, w-(w)/3-100, 5 , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0) 
            
            
            
            
            
            
            
            
            
            # DELETE EVENT SHOR KEY #
            
            allowdelete = False
            if not self.deletelastframe:
                allowdelete = True
            
            
            if 65535 in self.keys: #and allowdelete
                
                
                
                if self.event_select < len(self.FILE.events)  and allowdelete  and self.tool == "select":
                    
                    self.FILE.event_delete(self.event_select)
                
                    self.event_select = False
                    self.deletelastframe = True
                    
            else:
                self.deletelastframe = False
                
            
            
            
            
            
            
            
            
            
                
                
            ##### OTHER SIDE PANEL ####
            
            
            
            
            
            
            
            
            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#5c5c5c"))
            widget.window.draw_rectangle(xgc, True, w-(w)/3, 0, (w)/3, h) 
            
            
            
            
            
            Pstart = w-(w)/3
            Ppart = (w)/3
            
            
            
            
            
            
            
            
            ##### SCENE TEXT ####
            
            
            self.event_select # number of current event
            self.scene_select # number of current scene inside the event
            self.shotsSCROLL  # pixel to scroll to in the shotlist
            
            shotlistlength = 20
           
           
           
            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#494949"))   #7e5349
            widget.window.draw_rectangle(xgc, True, Pstart, 220, Ppart, h-220)
                    
                    
            #mark for faster moves
            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#4F4F4F"))
            widget.window.draw_rectangle(xgc, True, w-50, 220, 200, h-220)
            
            #mark for faster moves
            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#575757"))
            widget.window.draw_rectangle(xgc, True, w-50, 220, 200, 50)
            
            widget.window.draw_rectangle(xgc, True, w-50, h-50, 200, 50)
            
            anyscenedata = False
            
            for ind, i in enumerate(self.shotsDATA):
                #print i
                anyscenedata = True
                
                
                self.imgAT.append("")
                
                shotname, story, pixbuf, blends = i
                
                
                    
                    
                    
                    
                for b in story.split("\n"):
                    ctx.set_source_rgb(1,1,1)
                    ctx.set_font_size(15)
                    ctx.move_to( Pstart+20, 15+shotlistlength+220+self.shotsSCROLL)
                    ctx.show_text(b)
                    shotlistlength = shotlistlength + 15
                
                
                
                    
                    
                    
                if shotname:    
                    
                    if os.path.exists(self.pf+"/"+shotname):
                        # CHECKING THAT ALL SUBFOLDERS EXIST TOO
                        
                        
                        # storyboard , opengl, test_rnd, rendered, extra
                        
                        if os.path.exists(self.pf+"/"+shotname+"/storyboard") == False:
                            os.mkdir(self.pf+"/"+shotname+"/storyboard")
                        if os.path.exists(self.pf+"/"+shotname+"/opengl") == False:
                            os.mkdir(self.pf+"/"+shotname+"/opengl")
                        if os.path.exists(self.pf+"/"+shotname+"/test_rnd") == False:
                            os.mkdir(self.pf+"/"+shotname+"/test_rnd")
                        if os.path.exists(self.pf+"/"+shotname+"/rendered") == False:
                            os.mkdir(self.pf+"/"+shotname+"/rendered")
                        if os.path.exists(self.pf+"/"+shotname+"/extra") == False:
                            os.mkdir(self.pf+"/"+shotname+"/extra")
                    
                    else:
                        
                        self.shotsDATA[ind][2] = "None"
                    
                    shotlistlength = shotlistlength + 10
                    
                    
                    # TRY TO FIND A PICTURE
                    
                    img = "None"
                    
                    if pixbuf == False and shotlistlength+220+self.shotsSCROLL+self.empty_frame.get_height() > 220 and shotlistlength+220+self.shotsSCROLL < h:
                    
                        for folder in ["rendered", "test_rnd", "opengl", "storyboard", "extra"]:
                            
                            for L in os.walk(self.pf+"/"+shotname+"/"+folder):
                                
                                for FILE in L[2]:
                                
                                     
                                    
                                    print FILE
                                        
                                    for F in fileformats.images:   ### WHAT IF FOUND AN IMAGE
                                            
                                        if FILE.lower().endswith(F):
                                    
                                            img = gtk.gdk.pixbuf_new_from_file(thumbnailer.thumbnail(self.pf+"/"+shotname+"/"+folder+"/"+FILE, self.empty_frame.get_width(),self.empty_frame.get_height()))
                                            
                                            
                                            self.imgAT[ind] = shotname+"/"+folder+"/"+FILE
                                            
                                            break
                                    if img != "None":
                                        break
                                    
                                    for F in fileformats.videos:  ### WHAT IF FOUND A VIDEO
                                            
                                        if FILE.lower().endswith(F):
                                    
                                            img = gtk.gdk.pixbuf_new_from_file(thumbnailer.videothumb(self.pf+"/"+shotname+"/"+folder+"/"+FILE, self.empty_frame.get_width(),self.empty_frame.get_height()))
                                            
                                            self.imgAT[ind] = shotname+"/"+folder+"/"+FILE
                                            
                                            break  
                                        
                                if img != "None":
                                    break        
                                        
                            if img != "None":
                                break                    
                                            
                                        
                                    
                        
                                    
                        #if img == "None":
                            
                        
                                
                        self.shotsDATA[ind][2] = img # NO IMAGE FOUND
                    
                    
                    # GIVE UP
                    
                    
                    
                    elif pixbuf == "None" or pixbuf == False:
                    
                        
                            
                        #print "SHOTFOLDER", shotname
                        
                        if shotlistlength+220+self.shotsSCROLL+self.empty_frame.get_height() > 220 and shotlistlength+220+self.shotsSCROLL < h: # IF IN FRAME
                            
                            picW = Pstart+Ppart/2-self.empty_frame.get_width()/2
                            
                            widget.window.draw_pixbuf(None, self.empty_frame, 0, 0, picW, shotlistlength+220+self.shotsSCROLL , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
                        
                        shotlistlength = shotlistlength + self.empty_frame.get_height()
                    
                    
                    else:   ##### IF THE IMAGE ACTUALLY WAS FOUND
                        
                        if shotlistlength+220+self.shotsSCROLL+pixbuf.get_height() > 220 and shotlistlength+220+self.shotsSCROLL < h: # IF IN FRAME
                            
                            picW = Pstart+Ppart/2-pixbuf.get_width()/2
                            
                            
                            # MOUSE OVER
                            if mx in range(picW, picW+pixbuf.get_width()) and my in range(shotlistlength+220+self.shotsSCROLL, shotlistlength+220+self.shotsSCROLL+pixbuf.get_height()):
                                
                                tooltip = self.imgAT[ind]
                                
                                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#e47649"))
                                widget.window.draw_rectangle(xgc, True, picW -3, shotlistlength+220+self.shotsSCROLL -3, pixbuf.get_width()+6, pixbuf.get_height()+6)
                                
                                # get mouse to show the hand
                                widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))
                                
                                if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active() and my in range(220, h) :
                                    
                                    
                                    
                                    os.system("xdg-open "+self.pf+"/"+(self.imgAT[ind]))
                                
                            
                            
                            widget.window.draw_pixbuf(None, pixbuf, 0, 0, picW, shotlistlength+220+self.shotsSCROLL , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
                        
                        shotlistlength = shotlistlength + pixbuf.get_height()
                    
                    
                    
                    
                    shotlistlength = shotlistlength + 5
                    
                    
                    if os.path.exists(self.pf+"/"+shotname) == False: # IF FOLDER DOES NOT EXISIS
                        
                        # MOUSE OVER
                        if mx in range(Pstart, w) and my in range(shotlistlength+220+self.shotsSCROLL, shotlistlength+220+self.shotsSCROLL+20):
                            
                            tooltip = "Generate Shot's Folders \n\n Every shot can have a directory\nin /rnd folder to work\non the shot directly,\ncreate blend files,\nhold footage."
                            
                            # get mouse to show the hand
                            widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))
                            
                            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#5c5c5c"))
                            widget.window.draw_rectangle(xgc, True, Pstart, shotlistlength+220+self.shotsSCROLL, Ppart, 23)
                            
                            if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active() and my in range(220, h) :
                                
                                os.makedirs(self.pf+"/"+shotname)
                            
                            
                        
                        # DRAW BUTTON
                        
                        widget.window.draw_pixbuf(None, self.foldericon, 0, 0, Pstart+10, shotlistlength+220+self.shotsSCROLL , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
                        
                        ctx.set_source_rgb(1,1,1)
                        ctx.set_font_size(15)
                        ctx.move_to( Pstart+50, 15+shotlistlength+220+self.shotsSCROLL+2)
                        ctx.show_text("Generate Shot's Folders")
                        
                        
                        
                        
                        
                        
                    else:                                             # IF FOLDER EXISTS
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        # MAIN SHOT FOLDER 
                        
                        
                        
                        
                        # MOUSE OVER
                        if mx in range(Pstart, w) and my in range(shotlistlength+220+self.shotsSCROLL, shotlistlength+220+self.shotsSCROLL+20):
                            
                            tooltip = "/"+shotname
                            
                            # get mouse to show the hand
                            widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))
                            
                            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#5c5c5c"))
                            widget.window.draw_rectangle(xgc, True, Pstart, shotlistlength+220+self.shotsSCROLL, Ppart, 23)
                            
                            if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active() and my in range(220, h):
                                
                                os.system("nautilus "+self.pf+"/"+shotname)
                            
                            
                        
                        # DRAW BUTTON
                        
                        widget.window.draw_pixbuf(None, self.foldericon, 0, 0, Pstart+10, shotlistlength+220+self.shotsSCROLL , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
                        
                        ctx.set_source_rgb(1,1,1)
                        ctx.set_font_size(15)
                        ctx.move_to( Pstart+50, 15+shotlistlength+220+self.shotsSCROLL+2)
                        ctx.show_text("Open Shot's Folder")
                        
                        
                        
                        
                        # SPACE
                        shotlistlength = shotlistlength + 40
                        
                        
                        
                        # storyboard
                        
                        
                        
                        
                        # MOUSE OVER
                        if mx in range(Pstart, w-Ppart/2) and my in range(shotlistlength+220+self.shotsSCROLL, shotlistlength+220+self.shotsSCROLL+20):
                            
                            
                            
                            # get mouse to show the hand
                            widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))
                            
                            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#5c5c5c"))
                            widget.window.draw_rectangle(xgc, True, Pstart, shotlistlength+220+self.shotsSCROLL, Ppart/2, 23)
                            
                            if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active() and my in range(220, h):
                                
                                os.system("nautilus "+self.pf+"/"+shotname+"/storyboard")
                            
                            
                        
                        # DRAW BUTTON
                        
                        widget.window.draw_pixbuf(None, self.foldericon, 0, 0, Pstart+10, shotlistlength+220+self.shotsSCROLL , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
                        
                        ctx.set_source_rgb(1,1,1)
                        ctx.set_font_size(15)
                        ctx.move_to( Pstart+50, 15+shotlistlength+220+self.shotsSCROLL+2)
                        ctx.show_text("storyboard")
                        
                        
                        
                        
                        # opengl
                        
                        
                        
                        
                        # MOUSE OVER
                        if mx in range(Pstart+Ppart/2, w) and my in range(shotlistlength+220+self.shotsSCROLL, shotlistlength+220+self.shotsSCROLL+20):
                            
                            
                            
                            # get mouse to show the hand
                            widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))
                            
                            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#5c5c5c"))
                            widget.window.draw_rectangle(xgc, True, Pstart+Ppart/2, shotlistlength+220+self.shotsSCROLL, Ppart, 23)
                            
                            if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active() and my in range(220, h):
                                
                                os.system("nautilus "+self.pf+"/"+shotname+"/opengl")
                            
                            
                        
                        # DRAW BUTTON
                        
                        widget.window.draw_pixbuf(None, self.foldericon, 0, 0, Pstart+10+Ppart/2, shotlistlength+220+self.shotsSCROLL , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
                        
                        ctx.set_source_rgb(1,1,1)
                        ctx.set_font_size(15)
                        ctx.move_to( Pstart+50+Ppart/2, 15+shotlistlength+220+self.shotsSCROLL+2)
                        ctx.show_text("opengl")
                        
                        
                        # SPACE
                        shotlistlength = shotlistlength + 20
                        
                        # test_rnd
                        
                        
                        
                        
                        # MOUSE OVER
                        if mx in range(Pstart, w-Ppart/2) and my in range(shotlistlength+220+self.shotsSCROLL, shotlistlength+220+self.shotsSCROLL+20):
                            
                            
                            
                            # get mouse to show the hand
                            widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))
                            
                            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#5c5c5c"))
                            widget.window.draw_rectangle(xgc, True, Pstart, shotlistlength+220+self.shotsSCROLL, Ppart/2, 23)
                            
                            if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active() and my in range(220, h):
                                
                                os.system("nautilus "+self.pf+"/"+shotname+"/test_rnd")
                            
                            
                        
                        # DRAW BUTTON
                        
                        widget.window.draw_pixbuf(None, self.foldericon, 0, 0, Pstart+10, shotlistlength+220+self.shotsSCROLL , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
                        
                        ctx.set_source_rgb(1,1,1)
                        ctx.set_font_size(15)
                        ctx.move_to( Pstart+50, 15+shotlistlength+220+self.shotsSCROLL+2)
                        ctx.show_text("test_rnd")
                        
                        
                        
                        
                        # rendered
                        
                        
                        
                        
                        # MOUSE OVER
                        if mx in range(Pstart+Ppart/2, w) and my in range(shotlistlength+220+self.shotsSCROLL, shotlistlength+220+self.shotsSCROLL+20):
                            
                            
                            
                            # get mouse to show the hand
                            widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))
                            
                            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#5c5c5c"))
                            widget.window.draw_rectangle(xgc, True, Pstart+Ppart/2, shotlistlength+220+self.shotsSCROLL, Ppart, 23)
                            
                            if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active() and my in range(220, h):
                                
                                os.system("nautilus "+self.pf+"/"+shotname+"/rendered")
                            
                            
                        
                        # DRAW BUTTON
                        
                        widget.window.draw_pixbuf(None, self.foldericon, 0, 0, Pstart+10+Ppart/2, shotlistlength+220+self.shotsSCROLL , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
                        
                        ctx.set_source_rgb(1,1,1)
                        ctx.set_font_size(15)
                        ctx.move_to( Pstart+50+Ppart/2, 15+shotlistlength+220+self.shotsSCROLL+2)
                        ctx.show_text("rendered")
                        
                        
                        # SPACE
                        shotlistlength = shotlistlength + 40
                        
                        # extra
                        
                        
                        
                        
                        # MOUSE OVER
                        if mx in range(Pstart, w) and my in range(shotlistlength+220+self.shotsSCROLL, shotlistlength+220+self.shotsSCROLL+20):
                            
                            
                            
                            # get mouse to show the hand
                            widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))
                            
                            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#5c5c5c"))
                            widget.window.draw_rectangle(xgc, True, Pstart, shotlistlength+220+self.shotsSCROLL, Ppart, 23)
                            
                            if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active() and my in range(220, h):
                                
                                os.system("nautilus "+self.pf+"/"+shotname+"/extra")
                            
                            
                        
                        # DRAW BUTTON
                        
                        widget.window.draw_pixbuf(None, self.foldericon, 0, 0, Pstart+10, shotlistlength+220+self.shotsSCROLL , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
                        
                        ctx.set_source_rgb(1,1,1)
                        ctx.set_font_size(15)
                        ctx.move_to( Pstart+50, 15+shotlistlength+220+self.shotsSCROLL+2)
                        ctx.show_text("extra")
                        
                        
                        # SPACE
                        shotlistlength = shotlistlength + 40
                        
                        
                        ###### BLEND FILES ######
                        
                        # MAKING SURE THERE IS BLENDFILES DATA LOADED
                        if blends == False:
                            blends = []
                            for FILE in os.listdir(self.pf+"/"+shotname):   
                                
                                if FILE.lower().endswith(".blend"):
                                    print FILE, "blend found"
                                    blends.append([FILE, False])
                                    
                            
                            
                            self.shotsDATA[ind][3] = blends
                        
                        # Drawing something to the screen
                        
                        
                        #getting mesurmets
                        
                        cellsize = 160 # pixels
                        
                        xcells = (Ppart/cellsize)-1
                        
                        xstep = 0
                        
                        #print self.shotsDATA[ind][3]
                        
                        for BInd, blend in enumerate(blends): 
                            
                            BName, BPic =  blend
                            
                            
                            # TEST CELL
                            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#000"))
                            #widget.window.draw_rectangle(xgc, False, Pstart+20+(cellsize*xstep), shotlistlength+220+self.shotsSCROLL, cellsize, cellsize)
                            
                            
                            #IF IN FRAME
                            if shotlistlength+220+self.shotsSCROLL+20+cellsize-40 > 220 and shotlistlength+220+self.shotsSCROLL+20 < h: # IF IN FRAME
                                
                                
                                ctx.set_source_rgb(1,1,1)
                                ctx.set_font_size(10)
                                ctx.move_to( Pstart+20+(cellsize*xstep)+15, shotlistlength+220+self.shotsSCROLL+cellsize-20)
                                ctx.show_text(BName)
                                
                                
                                # MOUSE OVER BLENDFILE
                                if mx in range(Pstart+20+(cellsize*xstep)+20, Pstart+20+(cellsize*xstep)+20+cellsize-60) and my in range(shotlistlength+220+self.shotsSCROLL+20, shotlistlength+220+self.shotsSCROLL+20+cellsize-60):
                                    
                                    tooltip = "Open Blendfile\n"+BName
                                    
                                    # get mouse to show the hand
                                    widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))
                                    
                                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#e47649"))
                                    widget.window.draw_rectangle(xgc, True, Pstart+20+(cellsize*xstep)+15, shotlistlength+220+self.shotsSCROLL+15, cellsize-50, cellsize-50)
                            
                                    if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active() and my in range(220, h):
                                        
                                        os.system("xdg-open "+self.pf+"/"+shotname+"/"+BName)
                                    
                                    
                                    
                                
                                    
                                ##### RENDER BUTTON ####
                                
                                # MOUSE OVER
                                if mx in range(Pstart+20+(cellsize*xstep)+20+110, Pstart+20+(cellsize*xstep)+20+130) and my in range(shotlistlength+220+self.shotsSCROLL+20, shotlistlength+220+self.shotsSCROLL+40):
                                    
                                    tooltip = "Render The File"
                                    
                                    # get mouse to show the hand
                                    widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))
                                    
                                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#5c5c5c"))
                                    widget.window.draw_rectangle(xgc, True, Pstart+20+(cellsize*xstep)+20+110, shotlistlength+220+self.shotsSCROLL+20, 20, 20)
                                    
                                    if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active() and my in range(220, h):
                                        
                                        
                                        # SHOWING WATCH CURSOR
                                        
                                        widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
                                        while gtk.events_pending():
                                            gtk.main_iteration()
                                        
                                        
                                        
                                        def ee(shotname, BName):
                                            
                                            dialogs.rendersettings(self.pf, shotname+"/"+BName)
                                        glib.timeout_add(10, ee, shotname, BName)
                                
                                widget.window.draw_pixbuf(None, self.render, 0, 0, Pstart+20+(cellsize*xstep)+20+110, shotlistlength+220+self.shotsSCROLL+20 , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)   
                                
                                
                                ##### COPY BUTTON ####
                                
                                # MOUSE OVER
                                if mx in range(Pstart+20+(cellsize*xstep)+20+110, Pstart+20+(cellsize*xstep)+20+130) and my in range(shotlistlength+220+self.shotsSCROLL+50, shotlistlength+220+self.shotsSCROLL+90):
                                    
                                    tooltip = "Copy Blendfile to ClipBoard"
                                    
                                    # get mouse to show the hand
                                    widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))
                                    
                                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#5c5c5c"))
                                    widget.window.draw_rectangle(xgc, True, Pstart+20+(cellsize*xstep)+20+110, shotlistlength+220+self.shotsSCROLL+50, 20, 20)
                                    
                                    if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active() and my in range(220, h):
                                        
                                        self.BLboard = self.pf+"/"+shotname+"/"+BName
                                
                                widget.window.draw_pixbuf(None, self.copy, 0, 0, Pstart+20+(cellsize*xstep)+20+110, shotlistlength+220+self.shotsSCROLL+50 , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)   
                                   
                                
                                
                                
                                
                                ############    L    O    G   O  ################
                                
                                
                                
                                
                                
                                
                                
                                
                                # TRY TO LOAD THE LOGO
                                
                                
                                if BPic == False:
                                    
                                    try:
                                        BPic = gtk.gdk.pixbuf_new_from_file(thumbnailer.blenderthumb(self.pf+"/"+shotname+"/"+BName, 100,100))
                                    except:
                                        BPic = "None"
                                    
                                    self.shotsDATA[ind][3][BInd][1] = BPic
                                
                                
                                if BPic == False or BPic == "None":
                                
                                
                                
                                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#FFF"))
                                    widget.window.draw_rectangle(xgc, True, Pstart+20+(cellsize*xstep)+20, shotlistlength+220+self.shotsSCROLL+20, cellsize-60, cellsize-60)
                            
                                else:
                                    
                                    widget.window.draw_pixbuf(None, BPic, 0, 0, Pstart+20+(cellsize*xstep)+20, shotlistlength+220+self.shotsSCROLL+20 , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
                                
                            
                            xstep = xstep + 1
                            
                            if xstep > xcells:
                                xstep = 0
                                shotlistlength = shotlistlength + cellsize
                        
                        
                        
                        shotlistlength = shotlistlength + cellsize
                        
                        
                    
                        shotlistlength = shotlistlength + 10
                        
                        
                        
                        ### PASTE BLEND FILE BUTTON ###
                        
                        
                        if len(self.BLboard) > 0:
                            
                            
                            # MOUSE OVER
                            if mx in range(Pstart, w) and my in range(shotlistlength+220+self.shotsSCROLL, shotlistlength+220+self.shotsSCROLL+20):
                                
                                tooltip = "Paste Blend File\n"+self.BLboard
                                
                                # get mouse to show the hand
                                widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))
                                
                                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#5c5c5c"))
                                widget.window.draw_rectangle(xgc, True, Pstart, shotlistlength+220+self.shotsSCROLL, Ppart, 23)
                                
                                if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active() and my in range(220, h):
                                    
                                    widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
                                
                                    while gtk.events_pending():
                                        gtk.main_iteration()
                                    
                                    
                                    
                                    
                                    def ee(shotname):
                                
                                        Pname = ""
                                        Pname = dialogs.PickName(self.BLboard[self.BLboard.rfind("/")+1:])
                                    
                                        if Pname != "":
                                            
                                            if Pname.endswith(".blend") == False:
                                                Pname = Pname + ".blend"
                                            
                                            if Pname not in os.listdir(self.pf+"/"+shotname):
                                            
                                                print shotname
                                                fr = open(self.BLboard, "r")
                                                to = open(self.pf+"/"+shotname+"/"+str(Pname), "w")
                                                to.write(fr.read())
                                                to.close()
                                                
                                                
                                                
                                                #REFRASHING
                                                
                                                try:
                                                    scnDATA = self.FILE.get_scenes_data()
                                                    scenestory = scnDATA[self.event_select][self.scene_select][3]
                                                    self.shotsDATA = get_shots(scenestory, scnDATA[self.event_select][self.scene_select][1])
                                                except:
                                                    print "scene loading error"
                                    glib.timeout_add(10, ee, shotname)
                                        
                                        
                            
                            widget.window.draw_pixbuf(None, self.paste, 0, 0, Pstart+10, shotlistlength+220+self.shotsSCROLL , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
                            
                            ctx.set_source_rgb(1,1,1)
                            ctx.set_font_size(15)
                            ctx.move_to( Pstart+50, 15+shotlistlength+220+self.shotsSCROLL-2)
                            ctx.show_text(self.BLboard[self.BLboard.rfind("/")+1:])
                            
                            shotlistlength = shotlistlength + 23
                        
                        
                        
                        
                        ### ADD BLEND FILE BUTTON ###
                        
                        # MOUSE OVER
                        if mx in range(Pstart, w) and my in range(shotlistlength+220+self.shotsSCROLL, shotlistlength+220+self.shotsSCROLL+20):
                            
                            tooltip = "Create New, Blank\nBlend File"
                            
                            # get mouse to show the hand
                            widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))
                            
                            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#5c5c5c"))
                            widget.window.draw_rectangle(xgc, True, Pstart, shotlistlength+220+self.shotsSCROLL, Ppart, 23)
                            
                            if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active() and my in range(220, h):
                                
                                
                                
                                
                                def ee(shotname):
                                    
                                    Pname = ""
                                    Pname = dialogs.PickName("New_File.blend")
                                
                                    if Pname != "":
                                        
                                        if Pname.endswith(".blend") == False:
                                            Pname = Pname + ".blend"
                                        
                                        if Pname not in os.listdir(self.pf+"/"+shotname):
                                            print shotname
                                            fr = open(self.pf+"/py_data/new_file/empty.blend", "r")
                                            to = open(self.pf+"/"+shotname+"/"+str(Pname), "w")
                                            to.write(fr.read())
                                            to.close()
                                            
                                            
                                            
                                            #REFRASHING
                                            
                                            try:
                                                scnDATA = self.FILE.get_scenes_data()
                                                scenestory = scnDATA[self.event_select][self.scene_select][3]
                                                self.shotsDATA = get_shots(scenestory, scnDATA[self.event_select][self.scene_select][1])
                                            except:
                                                print "scene loading error"
                                glib.timeout_add(10, ee, shotname) 
                                
                        widget.window.draw_pixbuf(None, self.plus, 0, 0, Pstart+10, shotlistlength+220+self.shotsSCROLL , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
                            
                        ctx.set_source_rgb(1,1,1)
                        ctx.set_font_size(15)
                        ctx.move_to( Pstart+50, 15+shotlistlength+220+self.shotsSCROLL-2)
                        ctx.show_text("Add New Blend File")
                        
                        shotlistlength = shotlistlength + 23
                    
                
                shotlistlength = shotlistlength + 20
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#424242"))
                widget.window.draw_rectangle(xgc, True, Pstart, shotlistlength+220+self.shotsSCROLL, Ppart, 1)
                shotlistlength = shotlistlength + 20
                    
            
            if anyscenedata:
                
                shotlistlength = shotlistlength + 20
               
               
                
                if mx in range(Pstart+25, Pstart+25+Ppart-100) and my in range(shotlistlength+220+self.shotsSCROLL, shotlistlength+220+self.shotsSCROLL+200):
                    
                    
                    tooltip = "Create a new shot"
                            
                    # get mouse to show the hand
                    widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))
                    
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#5c5c5c"))
                    
                    
                    if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active() and my in range(220, h): # IF CLICKED
                    
                        
                        def justdoit(v=None):
                            sae = dialogs.event(name, story, self.FILE, self.event_select)
                            sae.add_shot()
                        
                            #REFRASHING
                                            
                            try:
                                scnDATA = self.FILE.get_scenes_data()
                                scenestory = scnDATA[self.event_select][self.scene_select][3]
                                self.shotsDATA = get_shots(scenestory, scnDATA[self.event_select][self.scene_select][1])
                            except:
                                print "scene loading error"
                        
                        
                        glib.timeout_add(10, justdoit)
                    
                        
                    
                else:
                
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#424242"))
                widget.window.draw_rectangle(xgc, True, Pstart+25, shotlistlength+220+self.shotsSCROLL, Ppart-100, 200)
                
                widget.window.draw_pixbuf(None, self.plus, 0, 0, Pstart+Ppart/4, shotlistlength+220+self.shotsSCROLL+100 , -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
                            
                ctx.set_source_rgb(1,1,1)
                ctx.set_font_size(15)
                ctx.move_to( Pstart+Ppart/4+40, 15+shotlistlength+220+self.shotsSCROLL+100)
                ctx.show_text("Create New Shot")
                
                
                
                shotlistlength = shotlistlength + 250
            
            
            
            
            # SCROLL
            
            if mx in range(Pstart, w) and my in range(220, h):
                
                if self.mpy > my and "GDK_BUTTON2" in str(fx) and "GDK_BUTTON2" in str(self.mpf) and self.win.is_active():
                    
                    self.shotsSCROLL = self.shotsSCROLL + (my-self.mpy)
                    
                    if mx in range(w-50, w):
                        self.shotsSCROLL = self.shotsSCROLL + (my-self.mpy)*2
                
                if self.mpy < my and "GDK_BUTTON2" in str(fx) and "GDK_BUTTON2" in str(self.mpf) and self.win.is_active():
                    
                    self.shotsSCROLL = self.shotsSCROLL - (self.mpy-my)
                    
                    if mx in range(w-50, w):
                        self.shotsSCROLL = self.shotsSCROLL - (self.mpy-my)*2
            
            
            if self.shotsSCROLL < 0-shotlistlength+(h-220):
                self.shotsSCROLL = 0-shotlistlength+(h-220)
            
            if self.shotsSCROLL > 0:
                self.shotsSCROLL = 0
            
            
            if mx in range(w-50, w):
                if "GDK_BUTTON2" in str(fx):
                    if my in range(220, 220+50):
                    
                        self.shotsSCROLL = 0-shotlistlength+(h-220)
                    if my in range(h-50, h):
                         
                        self.shotsSCROLL = 0
            
            
            
            
            
            
            ###### TOP EVENT EDIT BIG FUCKING BUTTTON
            
            
            
            xgc.set_rgb_fg_color(gtk.gdk.color_parse("#5c5c5c"))
            widget.window.draw_rectangle(xgc, True, Pstart, 0, Ppart, 220) ##################
            
            # loading selected event to the side panel
            
            try:        
                
                event = self.FILE.events[self.event_select]
                
                name = event[3]
                story = event[4]
                
                
                
                # IF MOUSE OVER THE TEXT
                if mx in range(Pstart, w) and my in range(0, 220):
                    
                    
                    ### ARROW KEY    SLLLOOOOOOOWWWW
                    
                    if 65362 in self.keys:
                        self.event_text_scroll = self.event_text_scroll-0.3
                    if 65364 in self.keys:
                        self.event_text_scroll = self.event_text_scroll+0.3
                    
                    ### PG UP PG DOWN FAST
                    
                    
                    
                    
                    if 65365 in self.keys:
                        self.event_text_scroll = self.event_text_scroll-1
                    if 65366 in self.keys:
                        self.event_text_scroll = self.event_text_scroll+1
                    
                    
                    
                    # MOUSE SCROLL
                
                    if self.mpy > my and "GDK_BUTTON2" in str(fx) and "GDK_BUTTON2" in str(self.mpf) and self.win.is_active():
                        
                        self.event_text_scroll = self.event_text_scroll - ((my-self.mpy) / 35 )
                    
                    if self.mpy < my and "GDK_BUTTON2" in str(fx) and "GDK_BUTTON2" in str(self.mpf) and self.win.is_active():
                        
                        self.event_text_scroll = self.event_text_scroll + ((self.mpy-my) / 35 )
                    
                    
                    
                    
                    
                    
                    xgc.set_rgb_fg_color(gtk.gdk.color_parse("#757575"))
                    widget.window.draw_rectangle(xgc, True, Pstart, 0, Ppart, 220)
                    
                    # IF CLICKED
                    
                    if "GDK_BUTTON1" in str(fx) and "GDK_BUTTON1" not in str(self.mpf) and self.win.is_active():
                        
                        def ee(e=None):
                            editevent = dialogs.event(name, story, self.FILE, self.event_select)
                            editevent.edit()
                    
                        glib.timeout_add(10, ee)
                        
                    
                
                
                ctx.set_source_rgb(1,1,1)
                ctx.set_font_size(20)
                ctx.move_to( Pstart+20, 30)
                ctx.show_text(name)
                
                if self.event_text_scroll < 0:
                    self.event_text_scroll = 0
                if len( story.split("\n") )-9 < self.event_text_scroll:
                    self.event_text_scroll  = len( story.split("\n") )-9
                
                sclval = int(self.event_text_scroll)
                
                for LI, Line in enumerate(story.split("\n")[sclval:sclval+9]):
                    
                    
                    ctx.set_source_rgb(1,1,1)
                    ctx.set_font_size(15)
                    ctx.move_to( Pstart+20, 15*LI+20+50)
                    ctx.show_text(Line)
                ctx.set_source_rgb(.8,.8,.8)
                ctx.set_font_size(12)
                ctx.move_to( Pstart+20, 15*10+20+45)
                ctx.show_text("... Click To Read Full Version Or EDIT ...")
                
                
                
            
            except:
                pass
            
            
            
                
                
                
                
                
            
            
        
            
            
            
            ####################################
            
            
            ##### TOOLTIP
            
            
            
            if tooltip:
                
                b = 0
                for i in str(tooltip).split("\n"):
                    if len(i) > b:
                        
                        b = len(i)
                
                xsize = b*6+2
                ysize = len(str(tooltip).split("\n"))*11
                
                
                xgc.set_rgb_fg_color(gtk.gdk.color_parse("#424242"))
                widget.window.draw_rectangle(xgc, True, mx+10, my+10, xsize,ysize)
                
                
                for n, i in enumerate(str(tooltip).split("\n")):
                    
                    
                    
                    
                
                
                
                
                    ctx2.set_source_rgb(1,1,1)
                    ctx2.set_font_size(10)
                    ctx2.move_to( mx+11, my+20+(n*10))
                    ctx2.show_text(i)
                    
            
            
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
        
        
        ## GETTING BUTTON PRESS EVENTS
        def bpe( w, event):
            
            
            if event.keyval not in self.keys:
                self.keys.append( event.keyval )
            print self.keys
            
        def bre (w, event):    
            
            try:
                self.keys.remove( event.keyval )
            except:
                pass
            
            print self.keys
            
        self.win.connect("key_press_event", bpe)
        self.win.connect("key_release_event", bre)
        
        
        self.box.show_all() 




# BOS FILES LOADER AND WRITER



class bos:
    
    
    def __init__(self, filename):
        
        
        
        self.filename = filename
        
        if not os.path.exists(filename):
            self.new(filename)
        
        
        self.events = []
        self.arrows = []
        self.markers = []
        self.tree = [] # THIS IS THE PLACE WEHRE STORED THE [IND, NAME] of scenes in the connected line from START to END of the movie
        
    def new(self, name):
        
        make = open(name, "w")
        make.write("# BOS blender- organizer story")
        make.close()
    
    def clear_arrows(self):
        
        ## THIS FUNCTION WILL CLEAR ALL DUPLICATIONS IN ARROWS...
        ## USE IT IN EVERY ARROW ADDITION TO MAKE SURE THERE IS NO
        ## WEIRD PATHS OF ARROWS
        
        # REMOVING DOUBLE CONNECTION TO ONE POINT
        
        for num, arrow in enumerate(self.arrows):
            
            for num2, arrow2 in enumerate(self.arrows):
                
                
                if arrow[0] == arrow2[0] or arrow[1] == arrow2[1]:
                    
                    self.arrows[num] = arrow2
        
        
        
        
        
        
        # removing doubles
        
        tmp = []
        
        for i in self.arrows:
            if i not in tmp:
                tmp.append(i)
        self.arrows = tmp
        
        
        
        return self.arrows # JUST IN CASE
    
            
    # THIS WILL OUTPUT THE SCENES DATA OUT FROM ALL EVENTS
    def get_scenes_data(self):
        
        scenes = []  # [[ event, name, dots,  text ] ,...]
        
        for IND, event in enumerate(self.events):
            
            name = event[3]
            story = event[4]
            
            eventscenes  = []
            
            if "<scene>" in story and "</scene>" in story:
                    
                sa = story.count("<scene>") # COUNT AMOUNT OF SCENES
                
                ts = story
                
                dot = 0
                dots = []
                
                # getting the values of the dots
                for i in range(sa):
                    
                    dot = dot + ts.find("<scene>")
                    d = [dot]
                    
                    ts = ts[ts.find("<scene>"):]
                    dot = dot + ts.find("</scene>")+8
                    
                    
                    # Adding scenes to a list to process later
                    
                    scene_text = ts[7:ts.find("</scene>")]
                    
                    
                    
                    
                    
                    ts = ts[ts.find("</scene>")+8:]
                    
                    d.append(dot)
                    dots.append(d)
                    
                    if '"' in scene_text:
                        name = scene_text[scene_text.find('"')+1:scene_text.replace('"', " ", 1).find('"')]
                    else:
                        name = "Uknnown Scene"
                    
                    scene_text = scene_text.replace('"'+name+'"', "", 1)
                    
                    eventscenes.append(  [IND, name, d, scene_text]  )
            
            scenes.append(eventscenes)
        
        return scenes
    
        
    def load(self):
    
        
        self.events = []
        self.arrows = []
        self.markers = []
        
        openfile = open(self.filename, "r")
        openfile = openfile.read()
        
        
        if "<event>" in openfile and "</event>" in openfile:
            
            # GETTING THE LIST OF EVENTS
            ep = openfile[openfile.find("<event>"):openfile.rfind("</event>")+8]# EP stants for events parts
            
            
            for event in ep.split("</event>")[:-1]:
                event = event[event.find("<event>")+8:] # CLEAFIYING THE TEXT OF THE EVENT
                
                
                #EVENT NAME
                
                name = event[event.find('"')+1:event.replace('"'," ",1).find('"')]
                
                
                # COORDINATES
                
                coordtext = event[event.find('[')+1:event.find(']')]
                coordinates =  coordtext.split(",")
                
                # EVENT TEXT
                
                story = event[event.find(']')+2:-1]
                
                #making coordinates into FLOATS
                
                tmp = []
                
                for i in coordinates:   
                
                    tmp.append(float(i))
                
                coordinates = tmp
                
                coordinates.append(name)
                coordinates.append(story)
                
                self.events.append( coordinates )
        
        if "<arrow>" in openfile and "</arrow>" in openfile:
            
            
            # GETTING THE LIST OF ARROWS
            ap = openfile[openfile.find("<arrow>"):openfile.rfind("</arrow>")+8]# AP stants for arrow parts
                
            for arrow in ap.split("</arrow>")[:-1]:
                
                arrow = arrow[arrow.find("<arrow>")+7:]
                
                # getting 2 sides
                
                arrow = arrow.split(" --> ")   
                print arrow
                
                arr = []
                
                
                for i in arrow: 
                    
                    side = i.split(",")
                    side = [ int(side[0]), side[1][side[1].find('"')+1:side[1].replace('"'," ",1).find('"') ]]
                    
                    arr.append(side)
                
                self.arrows.append(arr)
        
        
        #### GETTING MARKERS
        
        if "<marker>" in openfile and "</marker>" in openfile:
            
            #GETTING THE LIST OF MARKERS
            
            mp = openfile[openfile.find("<marker>"):openfile.rfind("</marker>")+9]# MP stants for markers parts
            
            for marker in mp.split("</marker>")[:-1]:
                
                mark = []
                
                marker = marker[marker.find("<marker>")+8:].split(",")
                
                
                mark.append(float(marker[0]))
                mark.append(str(marker[1][marker[1].find('"')+1:marker[1].replace('"'," ",1).find('"') ]))
                
                self.markers.append(mark)
        
        #### GETTING CAMERA DIMENTIONS ####
        
        if "<camera>" in openfile and "</camera>" in openfile:
            
            camera = openfile[openfile.find("<camera>")+8:openfile.rfind("</camera>")].split(",")
            
            
            # clearing  the camera list
            tmp = []
            
            for i in camera:
                tmp.append(float(i))
            
            camera = tmp
            
            return camera #outputiing the camera data and shutting the fuck up
                
    
    
    
        return 0.0,0.0,1.0,20.0
    
    
    def event_delete(self, num):
        
        del self.events[num]
        
        
        
        
        # deleting all arrows connected
        
        new = []
        for n, i in enumerate(self.arrows):
            
            
            
            if i[0][0] == num or i[1][0] == num:
                
                pass
            else:
                
                new.append(i)
        
        
        self.arrows = new
        
        
        # REARANGE
        
        for n, i in enumerate(self.arrows):
            
            
            
            if i[0][0] > num:
            
                self.arrows[n][0][0] = i[0][0] - 1
            
            if i[1][0] > num:
            
                self.arrows[n][1][0] = i[1][0] - 1
        
        
        
        print "Trying to delete event", 
    
    def split(self, event, LETTER, END, PIXEL, scnIND):    
        print event, LETTER, END, PIXEL
        
        pos, size, Y, name, story = self.events[event]
        
        
        if END:
            first = [pos, PIXEL-pos, Y, name, story[:LETTER[1]]]
            last  = [PIXEL, size-(PIXEL-pos), Y, name+"_split", story[LETTER[1]:]]
        
        else:
            first = [pos, PIXEL-pos, Y, name, story[:LETTER[0]]]
            last  = [PIXEL, size-(PIXEL-pos), Y, name+"_split", story[LETTER[0]:]]
           
        
            
        
        
        
        
        
        
        # FIXING ALL THE ARROWS AS ALWAYS OMG WTF WHY
        
        oldDATA = self.get_scenes_data() #SAVE OLD LOCATIONS OF THINGS
        
        # ASSIGNING THE SHIT
        self.events[event] = first
        self.events.insert(event+1, last)
        
        
        newDATA = self.get_scenes_data() #GETTING NEW LOCATIONS
        
        #CLEARING THE newDATA and oldDATA
        
        old = []
        
        for e in oldDATA:   # for all events in the data
            for s in e: # for all the scenes in the event
                old.append([s[0],s[1]])
        
        new = []
        
        for e in newDATA:   # for all events in the data
            for s in e: # for all the scenes in the event
                new.append([s[0],s[1]])
        
        
        print "ARROWS BEFORE\n"
        for i in self.arrows:
            print i
        
        # GETTING THE SCNAGES ONTO THE ARROWS
        
        for AN, arrow in enumerate(self.arrows):
            
            for SN, side in enumerate(arrow):
                
                for DN, data in enumerate(old):
                    
                    if data == side:    
                        
                        self.arrows[AN][SN] = new[DN] 
                    
        
        print "ARROWS AFTER\n"
        for i in self.arrows:
            print i
        
        print "sncDATA\n"
        print oldDATA
        print
        print newDATA
        
        
            
            
        
        
    
    def save(self, px, py, sx, sy):
        
        savefile = open(self.filename, "w")
        
        savefile.write("<camera>"+str(px)+","+str(py)+","+str(sx)+","+str(sy)+"</camera>\n")
        
        #EVENTS
        for event in self.events:   
        
            savefile.write('<event>\n"'+str(event[3])+'"\n['+str(event[0])+","+str(event[1])+","+str(event[2])+"]\n"+str(event[4])+"\n</event>\n\n")
        
        #ARROWS
        
        for arrow in self.arrows:
            
            savefile.write('<arrow>'+str(arrow[0][0])+',"'+str(arrow[0][1])+'" --> '+str(arrow[1][0])+',"'+str(arrow[1][1])+'"</arrow>\n')
        
        
        for marker in self.markers:
            savefile.write('<marker>'+str(marker[0])+',"'+str(marker[1])+'"</marker>\n')
        
        
            
        savefile.close()
        
        print "SAVED TOO  "+self.filename
        
        return


def get_shots(story, scenename):
    
    
    LIST = []
    
    if "<shot>" in story and "</shot>" in story:
        
        sa = story.count("<shot>")
        
        ts = story
        
        for i in range(sa):
            
            LIST.append( [False, ts[:ts.find("<shot>")], False, False] )   #[scenename, "TEXT", pixbuf, blends]
    
    
            ts = ts[ts.find("<shot>")+6:]
            
            if ts.count('"') > 1:
                shotname = "rnd/"+scenename+"/"+ts[ts.find('"')+1:ts.replace('"', " ", 1).find('"')]
                
            else:
                shotname = "Unnamed"
                
            LIST.append( [shotname.replace(" ", "_"), ts[:ts.find("</shot>")], False, False] )
            ts = ts[ts.find("</shot>")+7:]
            
    
        LIST.append( [False, ts, False, False] )
    else:
        
        LIST.append( [False, story, False, False] )
    
    
    
    return LIST
    
    
    
def get_scenes_percentage(FILE):
    
    
    arrows = FILE.arrows
    scnDATA =  FILE.get_scenes_data()
    
    #trying to get whether the start actually connects to end
    linkchained = False
    
    linkchainpath = []
    
    startlink = False
    
    for i in FILE.arrows:
        
        if i[0][0] == -1:
            
            linkchainpath.append(i)
            startlink = True
            
            
    while startlink: # dangerous motherfucker
        
        found = False
        
        for i in FILE.arrows:
            
            
            
            if linkchainpath[-1][1] == i[0]:
                
                
                
                found = True
                linkchainpath.append(i)
                
                if i[1][0] == -1:
                    linkchained = True
                    break
            
        if found == False:
            break
    
    
    
    
    persantage = 1.0
    valueslist = []
    
    for event in scnDATA:
        for scene in event:
            LIST = []
            
            
            story = scene[3]
            scenename = scene[1]
            
            links = []
            for n in linkchainpath: 
                links.append(n[1])
            
            if [scene[0], scene[1]] in links:
            
                scenevalues = []
    
                if "<shot>" in story and "</shot>" in story:
                    
                    sa = story.count("<shot>")
                    
                    ts = story
                    
                    for i in range(sa):
                        
                        #LIST.append( [False, ts[:ts.find("<shot>")], False, False] )   #[scenename, "TEXT", pixbuf, blends]
                
                
                        ts = ts[ts.find("<shot>")+6:]
                        
                        if ts.count('"') > 1:
                            shotname = "rnd/"+scenename+"/"+ts[ts.find('"')+1:ts.replace('"', " ", 1).find('"')]
                            
                        else:
                            shotname = "Unnamed"
                            
                        LIST.append( [shotname.replace(" ", "_"), ts[:ts.find("</shot>")], False, False] )
                        ts = ts[ts.find("</shot>")+7:]
                        
                
                    #LIST.append( [False, ts, False, False] )
        
                if LIST == []:
                    
                    
                    
                    print "EMPTY", scenename
                    scenevalues.append(0)
                
                
                for i in LIST:
                    
                    try:
                    
                        if len(os.listdir(i[0]+"/rendered")) > 0:
                            scenevalues.append(1.0)
                        
                        elif len(os.listdir(i[0]+"/test_rnd")) > 0:
                            scenevalues.append(0.8) 
                        
                        elif len(os.listdir(i[0]+"/opengl")) > 0:
                            scenevalues.append(0.6) 
                            
                        elif len(os.listdir(i[0]+"/storyboard")) > 0:
                            scenevalues.append(0.4)
                        
                        elif len(os.listdir(i[0]+"/extra")) > 0:
                            scenevalues.append(0.2) 
                    except:
                        scenevalues.append(0.0) 
                     
                
                scenevalue = float(sum(scenevalues))/len(scenevalues)
                valueslist.append(scenevalue)
                     
    
    persantage = float(sum(valueslist))/len(valueslist)
    return persantage
    
    
    
    
    
    
    
    
    
    
    
    
        
    
    
    
    
