from Tkinter import *
import tkFont
import re 

import MyGui  as MG
import Pick # pick et pick et kolegram bour et bour et ratatam


import GuyVariables as G
import WorkVariables as W


    ##################
    ## 0/ Main Caller
    #################

def WindowInit():
  Title() 
  MainFrameMaker()  # Create MenuBar and MainPaned, TextFrame and DrawwindFrame

  MenuBarMaker()  # take G.MenuBar
  TextFrameMaker() # take G.TextPaned
  DrawingFrameMaker() # take G.DrawingFrame  

  Shortcuts() # take MG and parents  



def Title():
  G.parent.title('ABISM ('+"/".join(str(W.image_name).split("/")[-3:])+')')     #   Adaptative Background Interactive Strehl Meter') 

  # ICON
  import os.path
  if os.path.isfile(W.path+'/Icon/bato_chico.gif') :
    bitmap = PhotoImage(file =W.path+'/Icon/bato_chico.gif')
    G.parent.tk.call('wm', 'iconphoto', G.parent._w, bitmap)
  else : 
    if W.verbose > 3 : print " you have no beautiful icon because you didn't set the PATH in Abism.py "


def MainFrameMaker():  
  if G.geo_dic.has_key("parent") :
     G.parent.geometry(G.geo_dic["parent"]) 

  def Menu() : 
    G.MenuBar = Frame(G.parent,bg=G.bg[0]) 
    G.all_frame.append("G.MenuBar")
    G.MenuBar.pack(side=TOP, expand = 0 , fill = X ) 

  def Main() :
    G.MainPaned=PanedWindow(G.parent,orient=HORIZONTAL,**G.paned_dic)   #  1 container, the buttons and the rest, paned can be resize with the mouse.   
    G.all_frame.append("G.MainPaned")
    #G.MainPaned.bind("<Key>", callback) #toknow 
    G.MainPaned.pack(side=TOP, fill=BOTH,expand=1)

  def Text() : 
    G.TextPaned = PanedWindow(G.MainPaned,orient=VERTICAL,**G.paned_dic) ###
    G.all_frame.append("G.TextPaned") 
    if G.geo_dic.has_key("TextPaned"): 
      G.MainPaned.add(G.TextPaned,width=float(G.geo_dic["TextPaned"]))
    else : # including don't set width 
      G.MainPaned.add(G.TextPaned)

  def Draw() : 
     G.DrawPaned = PanedWindow(G.MainPaned,orient=VERTICAL,**G.paned_dic)#,width=650)
     G.all_frame.append("G.DrawPaned")
     if G.geo_dic.has_key("DrawPaned"): 
       G.MainPaned.add(G.DrawPaned,width=float(G.geo_dic["DrawPaned"]))
     else : # including don't set width 
       G.MainPaned.add(G.DrawPaned)

  Menu() ; Main() ; Text() ; Draw() 



    ################
    ## 1/  MENU 
    ###############"

def MenuBarMaker(): # CALLER   
  global args         # the args of "MenuButton"
  col=0
  args={"relief":FLAT, "width":G.menu_button_width ,"bg":G.bg[0]} 
  for i in [
    ["FileMenu", {"text":u"\u25be "+"File"}  ] ,  
    ["HelpMenu",  {"text":u'\u25be '+'Help'} ] ,  
    ["ConnectMenu",  {} ], 
    ["ScaleMenu",  {"text":u'\u25be '+'Scale'} ], 
    ["FitMenu",  {"text":u'\u25be '+'FitType'} ] ,
    ["AppearanceMenu",  {"text":u'\u25be '+'Appearance',"width":11} ] ,# width because apparence string too long  
    #["HideFrameMenu",  {"text":u"\u25c2"} ], 
    ] : 
      args.update( i[1] ) 
      button = globals()[i[0]]() # the actual CALL  
      button.grid(row=0,column=col,sticky="NW") 

      col+=1
    

def FileMenu():
  G.menu=Menubutton(G.MenuBar,**args)   
  G.menu.menu=Menu(G.menu,**G.submenu_args)

  G.menu.menu.add_command(label='Open',command=MG.Open)
  G.menu.menu.add_command(label='Save',command=MG.Save)        
  G.menu.menu.add_command(label='Display Header',command=MG.DisplayHeader) 
  G.menu.menu.add_command(label='Histogram',command=MG.Histopopo)        
  #G.menu.menu.add_command(label='Cube?',command=G.Cube)
  #G.menu.menu.add_command(label='More Info',command=MG.MoreInfo) 
  if not G.more_bool : G.menu.menu.add_command(label=u'\u25be '+'More Options',command=MoreWidget) 
  else :  G.menu.menu.add_command(label=u'\u25b4 '+'Less Options',command=MoreWidget) 


  G.menu['menu'] = G.menu.menu  
  return G.menu  


def HelpMenu():    
  G.help_menu=Menubutton(G.MenuBar,**args )  
  G.help_menu.menu=Menu(G.help_menu,**G.submenu_args)

  G.help_menu.menu.add_command(label='Tutorial',command=MG.Tutorial)
  G.help_menu.menu.add_command(label='PythonConsole',command=MG.PythonConsole) 

  if not G.cal_bool : 
     G.help_menu.menu.add_command(label=u'\u25be '+'Calculator', command=Calculator )
  else : # In case a crazy man wanna start with calculator 
     G.help_menu.menu.add_command(label=u'\u25b4 '+'Calculator', command=Calculator )
     Calculator() 
  G.help_menu['menu'] = G.help_menu.menu  

  return G.help_menu 


def ConnectMenu():  # responsible to connect key, mouse events   
  G.connect_menu=Menubutton(G.MenuBar,**args) 
  G.connect_menu.menu = Menu(G.connect_menu,**G.submenu_args)   

  lst = [ "PickOne",  "PickMany" ,"Binary Fit",  "Profile"  , "Stat" , "Ellipse" ,"No Pick" ] # PickOne is defined yet 
  for i in lst : 
    G.connect_menu.menu.add_command(label= i, command = lambda i=i : Pick.RefreshPick(i) )  

  
  G.connect_menu['text'] = u'\u25be ' + "PickOne" 
  G.connect_menu['menu'] = G.connect_menu.menu  

  return G.connect_menu


def ScaleMenu():	
  G.scale_menu=Menubutton(G.MenuBar,**args)  
  G.scale_menu.menu=Menu(G.scale_menu,**G.submenu_args)


  ###############"
  ## COLOR 
  def Color() : 
      if G.scale_menu_type== "cascade" : 
        color_menu = Menu(G.scale_menu,**G.submenu_args)  
      else : 
        color_menu = G.scale_menu.menu    
	color_menu.add_command(label="COLOR",bg=None,state=DISABLED) 
         # if we don't want cascade, we just add in the menu 

      G.cu_color=StringVar(); G.cu_color.set(G.scale_dic[0]["cmap"])
       # list display name and cmap name 
      


      ###########"
      # My colors 
      lst = [  ["Jet","jet"],['Black&White','bone'],['Spectral','spectral'], ["RdYlBu","RdYlBu"], ["BuPu","BuPu"] ]
      for i in lst :
        color_menu.add_radiobutton(label=i[0],        
          command=lambda i=i: MG.Scale(dic={"cmap":i[1]}),
          variable=G.cu_color,value=i[0]) # we use same value as label 	


      ########
      # Contour
      color_menu.add_command(label='Contour',   
          command=lambda  : MG.Scale(dic={"contour":'not a bool'})  )	


      #################
      # more colors
      more_color_menu = Menu(color_menu,**G.submenu_args) 
      num=0
      for i in G.all_cmaps : 
          num+=1
          more_color_menu.add_radiobutton(label=i,        
            command=lambda i=i: MG.Scale(dic={"cmap":i}),
            variable=G.cu_color,value=i) # we use same value as label 	
 
          if num%30==0  :
            
            more_color_menu.add_radiobutton(label=i,        
              command=lambda i=i : MG.Scale(dic={"cmap":i}),
              variable=G.cu_color,value=i,columnbreak=1) # we use same value as label 	
      color_menu.add_cascade(menu=more_color_menu,label="More colors",underline=0) 



      if G.scale_menu_type== "cascade" : 
         G.scale_menu.menu.add_cascade(menu=color_menu, underline=0,label="Color")
      else : 
         G.scale_menu.menu.add_command(columnbreak=1) 
    

  ##############
  ###" SCALE FUNCTION
  def Scale(): 
      if G.scale_menu_type== "cascade" : scale_menu = Menu(G.scale_menu,**G.submenu_args)  
      else : 
        scale_menu = G.scale_menu.menu    
	scale_menu.add_command(label="FCT",bg=None,state=DISABLED) 
      
      G.cu_scale=StringVar(); G.cu_scale.set("Lin")
      lst = [  ["Lin","x","linear"],["Sqrt","x**0.5","sqrt"],["Square","x**2","square"],["Log","np.log(x+1)/0.69","log"],["Arcsinh","","arcsinh" ]   ] # bite missing arcsinh 
      for i in lst :
        scale_menu.add_radiobutton(label=i[0]   ,
          command=lambda i=i : MG.Scale( dic={"fct":i[1],"stretch":i[2]}) , 
          variable=G.cu_scale,value=i[0]) # we use same value as label 	


      if G.scale_menu_type== "cascade" : 
         G.scale_menu.menu.add_cascade(menu=scale_menu, underline=0,label="Fct")
      else : 
         G.scale_menu.menu.add_command(columnbreak=1) 

  #G.bu_scale['menu'] = G.bu_scale.menu
  #G.bu_scale.bind("<Button-1>",lambda event : MG.Scale(dic={"tutorial":1,"fct":"truc"}) ) 


  ##############
  ##  CUT TYPE 
  def Cut() : 
      if G.scale_menu_type== "cascade" : cut_menu = Menu(G.scale_menu,**G.submenu_args)  
      else : 
        cut_menu = G.scale_menu.menu    
	cut_menu.add_command(label="CUT",bg=None,state=DISABLED) 

      G.cu_cut=StringVar(); G.cu_cut.set("RMS")
      # label , scale_cut_type, key, value 
      lst = [  ["RMS","sigma_clip","sigma",3],["99.95%","percent","percent",99.95], 
               ["99.9%","percent","percent",99.9], ["99.5%","percent","percent",99.5], 
               ["99%","percent","percent",99.], ["90%","percent","percent",90], 
               ["None","None","truc","truc"] ,
	       #["Manual","manual","truc","truc"] ,  ]
	       ] 
      for i in lst : 
        cut_menu.add_radiobutton(label=i[0],
          command=lambda i=i : MG.Scale(dic={"scale_cut_type":i[1],i[2]:i[3]}),
          variable=G.cu_cut,value=i[0]) # we use same value as label 	
      
      cut_menu.add_radiobutton(label="Manual",
          command= ManualCut,
          variable=G.cu_cut,value="Manual") # we use same value as label 	

      if G.scale_menu_type== "cascade" : 
         G.scale_menu.menu.add_cascade(menu=cut_menu, underline=0,label="Cut")
      else : 
         G.scale_menu.menu.add_command(columnbreak=1) 

  #G.bu_cut['menu'] = G.bu_cut.menu	
  #G.bu_cut.bind("<Button-1>",lambda event : MG.Scale(dic={"tutorial":1,"scale_cut_type":"truc"}) ) 
	
  Color() 
  Scale() 
  Cut() 
  G.scale_menu['menu'] = G.scale_menu.menu  

  return G.scale_menu


def FitMenu() : 
  G.fit_menu= Menubutton(G.MenuBar,**args) 
  G.fit_menu.menu=Menu(G.fit_menu,**G.submenu_args)

  G.cu_fit=StringVar(); G.cu_fit.set("Moffat")
  lst = [  ["Gaussian","Gaussian"], ["Moffat","Moffat"], ["Bessel", "Bessel1"], ["Gaussian_hole","Gaussian_hole"]  , ["None","None"] ] # Label in the menu; W.fit_type
  for i in lst :  
    G.fit_menu.menu.add_radiobutton(label=i[0],
      command=lambda i=i  : MG.FitType(i[1]),
      variable=G.cu_fit,value=i[0]) # we use same value as label 	

  G.fit_menu['menu'] = G.fit_menu.menu
  G.fit_menu.bind("<Button-1>",lambda event : MG.FitType("tutorial")   ) 

  return G.fit_menu


def AppearanceMenu() : 
  def CrazyColor() :
     import color_interactive
     color_interactive.Main()

  G.appearance_menu= Menubutton(G.MenuBar,**args) 
  G.appearance_menu.menu=Menu(G.appearance_menu,**G.submenu_args)

  G.cu_appearance=StringVar(); G.cu_appearance.set(G.bg[0])
  lst = [  "#d0d0d0",  "#d0d0d0",  "#d0d0d0","#ff0000","#00ff00","#0000ff","#ffff00","#ffb33b","#a000f3",  "#ffffff", "#d0d0d0","#000000"]  
  num=0
  for i in lst : 
      G.appearance_menu.menu.add_radiobutton(
            background=i,command= lambda i=i : BgCl(color=i)  , 
	    variable = G.cu_appearance, value = i  , 
	    ) 
      num+=1
      if num%3 ==0 and i !="#000000" : 
        G.appearance_menu.menu.add_command(columnbreak=1) 

  G.appearance_menu.menu.add_command(
            label="H\nS\nL", 
            background=G.bg[0],command=CrazyColor , 
	    ) 


  G.appearance_menu['menu'] = G.appearance_menu.menu
  G.appearance_menu.bind("<Button-1>",lambda event : MG.FitType("tutorial")   ) 

  return G.appearance_menu

def HideFrameMenu():  # read G.hidden_tex_bool 
  if G.hidden_text_bool : 
    G.bu_hide["text"]=u'\u25b8' # just need to change the text  

  else : # including not hidden
    if "bu_hile" in vars(G) : 
      G.bu_hide["text"]=u'\u25c2' # just need to change the text  
      
    else : 
      G.bu_hide = Button(G.MenuBar,
          command = (lambda : MG.Hide()) , **args) 
      G.bu_hide.pack(side=LEFT,expand=0)

  return G.bu_hide


    #################
    ## 2/  DrawPaned
    ##################

def DrawingFrameMaker() :  # receive G.DrawPaned 
  G.ImageFrame = Frame(G.DrawPaned,bg=G.bg[0])  #,width=100, height=100)
  G.all_frame.append("G.ImageFrame") 

  def Image(): 
    if G.geo_dic.has_key("ImageFrame"): 
      G.DrawPaned.add(G.ImageFrame,height=float(G.geo_dic["ImageFrame"]))
    else : # including don't set width 
      G.DrawPaned.add(G.ImageFrame)
    G.all_frame.append("G.ImageFrame") 

  def RightBottom(): 
    G.RightBottomPaned = PanedWindow(G.DrawPaned,orient=HORIZONTAL,**G.paned_dic)
    if G.geo_dic.has_key("RightBottomPaned"): targ={"height":float(G.geo_dic["RightBottomPaned"]) } 
    else : targ= {} 
    G.DrawPaned.add(G.RightBottomPaned,**targ)
    G.all_frame.append("G.RightBottomPaned") 

  def RightBottomSub() : #In RightBottomPaned 2 : FitFrame, ResultFrame (should be star frame) 
    def Fit() : 
      G.FitFrame = Frame(G.RightBottomPaned,bg=G.bg[0])
      if G.geo_dic.has_key("FitFrame"): targ={"width":float(G.geo_dic["FitFrame"]) }
      else : targ= {} 
      G.RightBottomPaned.add(G.FitFrame,**targ)
      G.all_frame.append("G.FitFrame") 

    def Result() : 
      G.ResultFrame = Frame(G.RightBottomPaned,bg=G.bg[0])
      if G.geo_dic.has_key("ResultFrame"): targ={"width":float(G.geo_dic["ResultFrame"]) }
      else : targ= {} 
      G.RightBottomPaned.add(G.ResultFrame,**targ)
      G.all_frame.append("G.ResultFrame") 

    Fit() ; Result() 

  Image() ; RightBottom() ; RightBottomSub() 


    ###########
    # 3/  TextPaned 
    ############


def TextFrameMaker() :
  def Top() :  
    G.LeftTopFrame = Frame(G.TextPaned,bg=G.bg[0]) ###
    G.all_frame.append("G.LeftTopFrame") 
    if G.geo_dic.has_key("LeftTopFrame"): 
      G.TextPaned.add(G.LeftTopFrame,height=int(G.geo_dic["LeftTopFrame"]))
      if W.verbose > 3 : print "I chose ", int(G.geo_dic["LeftTopFrame"]), " for height of LefTOPFRAME" 
    else : # including don't set width 
      G.TextPaned.add(G.LeftTopFrame)

  def Result(): # bottom  
    G.LeftBottomFrame = Frame(G.TextPaned,bg=G.bg[0]) ###
    G.all_frame.append("G.LeftBottomFrame") 
    if G.geo_dic.has_key("LeftBottomFrame"): 
      G.TextPaned.add(G.LeftBottomFrame,height=int(G.geo_dic["LeftBottomFrame"]))
    else : # including don't set width 
      G.TextPaned.add(G.LeftBottomFrame)

  def TopSub() : # call TxtButton1() 
    text_frame_list = []
    
    TextButton1() 
    
    G.LabelFrame=Frame(G.TextPaned,bg=G.bg[0]) 
    G.all_frame.append("G.LabelFrame") 
    G.LabelFrame.pack(side=TOP,expand=0,fill=X) 

     
  def BottomSub() : 

    Label(G.LeftBottomFrame,text="Results",**G.frame_title_arg).pack(side=TOP,anchor="w")
    G.AnswerFrame=Frame(G.TextPaned,bg=G.bg[0]) 
    G.all_frame.append("G.AnswerFrame") 
    G.AnswerFrame.pack(expand=0,fill=BOTH) 

  Top() ; Result() ; TopSub() ; BottomSub()  


def TextButton1():
  G.Button1Frame=Frame(G.LeftTopFrame,bg=G.bg[0]) 
  G.all_frame.append("G.Button1Frame") 
  G.Button1Frame.pack(side=TOP,expand=0,fill=X)
  
  G.Button1_1Frame=Frame(G.Button1Frame,bg=G.bg[0])# restart quit  
  G.all_frame.append("G.Button1_1Frame") 
  G.Button1_1Frame.pack(side=TOP,expand=0,fill=X)  

  G.Button1_2Frame=Frame(G.Button1Frame,bg=G.bg[0])# iamge parameters 
  G.all_frame.append("G.Button1_1Frame") 
  G.Button1_2Frame.pack(side=TOP,expand=0,fill=X)  


  # DEFINE BUTTON 
  G.bu_quit=Button(G.Button1_1Frame,text='QUIT',background=G.bu_quit_color, 
                  command=MG.Quit,**G.bu_arg)  # QUIT
  G.bu_restart=Button(G.Button1_1Frame,text='RESTART',background =G.bu_restart_color, command=MG.Restart, **G.bu_arg)                   # RESTART
  G.bu_manual=Button(G.Button1_2Frame,text=u'\u25be '+'ImageParameters',
                  background=G.bu_manual_color,command=ImageParameter,**G.bu_arg) #Manual M 

  
  for i in ( G.bu_quit,G.bu_restart) : i.pack(side=LEFT,expand=1,fill=X) 
  G.bu_manual.pack(expand=1,fill=X)
  if W.verbose > 3 : print "I pack the first buttons" 

  return G.Button1Frame  


def LabelDisplay(): # What do I know from header
  """ESO / not ESO 
  NAco/vlt
  Reduced/raw
  Nx x Ny x Nz
  WCS detected or not 
  """
  lst=[]
  # ESO 
  if W.head.company == "ESO" : lbl = "from ESO"
  else                  : lbl = "NOT from ESO"
  lst.append(lbl)

  #NACO/VLT
  if W.head.instrument == "NAOS+CONICA" : ins= "NaCo"
  else                             : ins= W.head.instrument
  tel= re.sub("-U.","",W.head.telescope.replace("ESO-","") ) # to delete ESO-  and -U4
  lbl = ins + " / "+ tel
  lst.append(lbl)

  #REDUCED ? 
  if "reduced_type" in vars(W.head) : 
     lbl=W.head.reduced_type
     lst.append(lbl)

  #Nx * Ny * Nz
  shape = list(W.Im0.shape[::-1]) # reverse, inverse, list order 
  if len(shape)==2 : 
     shape.append(1)
  lbl = "dim: (%i,%i)" % (shape[0],shape[1])
  lst.append(lbl)

  #WCS 
  if W.head.pywcs != None :
     try : 
       tmptmp = W.head.pywcs.wcs.cd
       lbl ="WCS detected"
     except : 
       lbl ="WCS NOT detected"
  else               : lbl ="WCS NOT detected"
  lst.append(lbl)

  for i in lst : 
     Label(G.LabelFrame,foreground='black',bg=G.bg[0],  
           text=i).pack(side=TOP,expand=0,fill=X)


    ######################
    ### 4/  Misery to Hide  #
    ######################

def ImageParameter():
  if G.tutorial:
               text="To measure the Strehl ratio I really need :\n"
               text+="-> Diameter of the telescope [in meters]\n"
               text+="-> Obstruction of the telescope [ in % of the area obstructed ]\n"
               text+="-> Wavelenght [ in micro meter ], the central wavelength of the band\n"
               text+="-> Pixel_scale [ in arcsec per pixel ]\n"
               text+="All the above parameters are used to get the diffraction pattern of the telescope because the peak of the PSF will be divided by the maximum of the diffraction patter WITH the same photometry to get the strehl.\n\n"
               text+="Put the corresponding values in the entry widgets. Then, to save the values, press enter i, ONE of the entry widget or click on ImageParamter button again.\n"
               text+="Note that these parameters should be readden from your image header. If it is not the case, you can send me an email or modify ReadHeader.py module." 
               MG.TutorialReturn({"title":"Image Parameters",
               "text":text
               }) 
               return 


  lst = [  ["Wavelength"+"*"+ " [um]:", "wavelength",99.] , 
	   ["Pixel scale" + "*"+ " [''/pix]: ","pixel_scale",99.],
           ["Diameter" +"*"+" [m]:","diameter",99.],  
	   #["Obstruction" + "*"++   "[%]:","obstruction",30],
	   ["Obstruction*" +  " [%]:","obstruction",0.],
	   ["Zero point [mag]: ","zpt",0.],
	   ["Exposure time [sec]: ","exptime",1.],
	   ]  # Label, variable , default value  
  def GetValue(event):
    for i in range(len(lst)): # lst is known due to the variable scope : a nested function inherits of the local variables of the parent function  
      vars(W.head)[lst[i][1]] = float(G.entries[i].get() ) 
    if not (W.head.wavelength==99. or  W.head.diameter==99. or W.head.obstruction==99 or W.head.pixel_scale==99.):
       ResetLabel()
       Label(G.LabelFrame,foreground='blue',bg=G.bg[0],  
           text="Ok : Image Parameter \n readen from header. \n Pick a star  \n ").pack(side=BOTTOM,expand=0,fill=X)
       if W.head.wavelength*1e-6/W.head.diameter/(W.head.pixel_scale/206265)<2 : 
          Label(G.LabelFrame,foreground='red',bg=G.bg[0], 
            text="WARNING : Bad pixelisation \n Use FWHM better than Strehl  \n ").pack(side=BOTTOM,  expand =1 , fill =X)
          

  if G.bu_manual["background"]==G.bu_manual_color:
    G.ManualFrame = Frame(G.LeftTopFrame,bg=G.bg[0]) ###
    G.all_frame.append("G.ManualFrame") 
    G.ManualFrame.pack(expand=0,fill=BOTH,side=TOP)  
    Label(G.ManualFrame,text="Parameters",**G.frame_title_arg).pack(side=TOP,anchor="w")
    G.ManualGridFrame=Frame(G.ManualFrame) 
    G.ManualGridFrame.pack(expand=0,fill=BOTH,side=TOP)  
    G.ManualGridFrame.columnconfigure(0,weight=1)
    G.ManualGridFrame.columnconfigure(1,weight=1)
   
    G.entries=[]
    r=0
    for i in lst : 
      l=Label(G.ManualGridFrame,text=i[0],font=G.font_param,bg=G.bg[0],justify=LEFT,anchor="nw")
      l.grid(row=r,column=0,sticky="NSEW")
      v= StringVar()
      e=Entry(G.ManualGridFrame, width=10,textvariable=v,font=G.font_param)
      if vars(W.head)[i[1]] == i[2] : 
        e["bg"]="#ff9090" 
      e.grid(row=r,column=1,sticky="NSEW")
      e.bind('<Return>',GetValue)
      v.set(vars(W.head)[i[1]])
      G.entries.append(v)
      r+=1
      

    G.bu_manual["background"]='green'
    G.bu_manual["text"]= u'\u25b4 '+'ImageParameters'
    return 


  elif G.bu_manual["background"]=='green':  #destroy manualFrame  and save datas
    GetValue("") # because receive event  
    G.ManualFrame.destroy()
    G.all_frame = [ x for x in G.all_frame if x!="G.ManualFrame" ] # remove MoreFrame
    G.bu_manual["background"]=G.bu_manual_color
    G.bu_manual["text"]=u'\u25be '+'ImageParameters'
    return
  return	  


def Calculator(): # receive LabelFrame
    if G.tutorial:
                   text="This button create a Calculator in the G.LabelFrame. You can put the cursor in the text entry and type with the keyboard and press enter to get the result or clisk on the button and '=' returns the answer. Numpy is automatically import as *"
		   text+="\n\nProgrammers a memory would be user firendly, but anyway, nobody will use this calculator, bc or python or awk are much  better..." 
		   MG.TutorialReturn({"title":"Calculator",
		   "text":text,
		   })
		   return     
    G.cal_bool = not G.cal_bool
    ResetLabel()
    if G.cal_bool : 
      import Calculator as Cal
      Cal.MyCalculator(G.LabelFrame) 
    # Change help menu label
    for i in range(1,10) : 
       j = G.help_menu.menu.entrycget(i,"label")
       if "Calculator" in j: 
         if G.cal_bool : G.help_menu.menu.entryconfig(i,label=u'\u25b4 '+'Calculator') 
	 else        :  G.help_menu.menu.entryconfig(i,label=u'\u25be '+'Calculator' )
	 break 
         
      
    return 

def ResetLabel(): 
  G.LabelFrame.destroy()
  G.LabelFrame = Frame(G.LeftTopFrame,bg=G.bg[0]) ###
  G.LabelFrame.pack(fill=X)


def Cube():
      if not W.cube_bool: 
        G.CubeFrame.destroy()
      else : 
        # FRAME
	G.CubeFrame = Frame(G.Button1Frame,bg=G.bg[0])
	G.CubeFrame.pack(side=TOP,expand=0,fill=X)
        Label(G.CubeFrame,text="Cube Number",**G.frame_title_arg).pack(side=TOP,anchor="w")
	G.CubeSelFrame=Frame(G.CubeFrame,bg=G.bg[0])
	G.CubeSelFrame.pack(side=TOP,expand=0,fill=X)
	
            # CUBE IMAGE SELECTION
        # LEFT
	G.bu_cubel=Button(G.CubeFrame,text = '<-',command=lambda:MG.CubeDisplay("-"))
	G.bu_cubel.pack(side=LEFT,expand=1,fill=X)

        # ENTRY
	G.cube_var = StringVar()
	G.cube_entry = Entry(G.CubeFrame, width=10,justify=CENTER,textvariable=G.cube_var)
	G.cube_var.set(W.cube_num)
	G.cube_entry.bind("<Return>",lambda x:MG.CubeDisplay("0"))
	G.cube_entry.pack(side=LEFT,expand=1,fill=X)

        # RIGHT 
	G.bu_cuber=Button(G.CubeFrame,text = '->',command=lambda:MG.CubeDisplay("+"))  
	    #G.bu_cuber.pack(side=LEFT,fill=X)
	G.bu_cuber.pack(side=LEFT,expand=1,fill=X)


      #W.cube_bool = not W.cube_bool	
      # we change cube bool in init image 
      return 


def MoreWidget(): # bite change esyer way the text 
  if G.more_bool ==1 : # close more frame
    MoreClose() 
 
  else :               # open more frame bite need to grid 
    G.more_bool = not G.more_bool # mean = 1 
    ##########""
    # FRAME
    G.MoreFrame = Frame(G.LeftTopFrame,bg=G.bg[0])  #create the more_staff Frame
    G.all_frame.append("G.MoreFrame") 
    G.MoreFrame.pack(side=TOP,expand=0,fill=X)

    Label(G.MoreFrame,text="More Options",**G.frame_title_arg).pack(side=TOP,anchor="w")

    G.MoreGridFrame = Frame(G.MoreFrame,bg=G.bg[0])  #create the more_staff Frame
    G.all_frame.append("G.MoreGridFrame") 
    G.MoreGridFrame.pack(side=TOP,expand=0,fill=X)
    G.MoreGridFrame.columnconfigure(0,weight=1)
    G.MoreGridFrame.columnconfigure(1,weight=1)
                                   
    def SubtractBackground(frame) : 
      G.bu_subtract_bg=Button(frame,text='SubstractBackground',  
                      background=G.bu_subtract_bg_color,command=MG.SubstractBackground,**G.bu_arg)    
      return G.bu_subtract_bg 
 

    def NoiseType(frame) : 
      G.menu_noise=Menubutton(frame,text=u'\u25be '+'Background',relief=RAISED, background=G.menu_noise_color,**G.bu_arg)  
      G.menu_noise.menu=Menu(G.menu_noise)
 
      G.cu_noise=StringVar(); G.cu_noise.set(W.noise_type) # bite 
      lst = [ ['Fit','fit'] , ["8Rects","8rects"]  , ['Manual',"manual" ],
              ["None","None"] ]
           #  ["InRectangle", "in_rectangle" ] ,
      for i in lst :
        G.menu_noise.menu.add_radiobutton(label=i[0]   ,
          command=lambda i=i : MG.WVarSet("noise_type",i[1]) , 
          variable=G.cu_noise,value=i[0]) # we use same value as label 	
 
      G.menu_noise['menu'] = G.menu_noise.menu
      return G.menu_noise
 
    
    def PhotType(frame)  : 
        G.menu_phot=Menubutton(frame,text=u'\u25be '+'Phot',relief=RAISED, background=G.menu_phot_color,**G.bu_arg)  
        G.menu_phot.menu=Menu(G.menu_phot)
 
        G.cu_phot=StringVar(); G.cu_phot.set(W.phot_type) # bite 
        lst =  [  [ 'Fit','fit'] , ['Encircled Energy','encircled_energy'],  ['Manual','manual'], ["Elliptical Aerture","elliptical_aperture"]    ]#,  ["Aperture", "Aperture"]  ]
        for i in lst :
          G.menu_phot.menu.add_radiobutton(label=i[0]   ,
            command=lambda i=i : MG.WVarSet("phot_type",i[1]) , 
            variable=G.cu_phot,value=i[1]) # we use same value as label 	
 
        G.menu_phot['menu'] = G.menu_phot.menu
	return G.menu_phot
 

    def Check(frame) : 
	myargs = { "anchor":"w","bg":G.bg[0],"fg":G.fg[0], "padx":0 ,  "pady":0 ,"highlightthickness":0 }
        ################
        # isoplanetism  
        G.iso_check = Checkbutton(frame, 
	       text="Anisoplanetism", variable=W.aniso_var,
               command=lambda :MG.FitType(W.fit_type),**myargs) # by default onvalue=1 
  
        G.same_check = Checkbutton(G.MoreGridFrame, 
	      text="Binary_same_psf", variable=W.same_psf_var,
              command = lambda : MG.FitType(W.fit_type),**myargs) 
 
        G.same_center_check = Checkbutton(G.MoreGridFrame, 
	      text="Saturated_same_center", variable=W.same_center_var,
              command= lambda: MG.FitType(W.fit_type),**myargs)  

	return G.iso_check, G.same_check, G.same_center_check 
      

    SubtractBackground(G.MoreGridFrame).grid(row=0,column=0,columnspan = 2,sticky="nswe")    
    NoiseType(G.MoreGridFrame).grid(row=1,column=0,sticky="nswe") 
    PhotType(G.MoreGridFrame).grid(row=1,column=1,sticky="nswe" ) 
    row=2
    for i in Check(G.MoreGridFrame) : 
      i.grid(row = row, column=0,columnspan = 2 ,sticky="nwse") 
      row+=1

    G.bu_close=Button(G.MoreGridFrame,text=u'\u25b4 '+'Close',background=G.bu_close_color,command=MoreClose,**G.bu_arg) 
    G.bu_close.grid(row=row,column=0,columnspan=2)         


def MoreClose():
       G.more_bool = not G.more_bool
       G.MoreFrame.destroy()      
       G.all_frame = [ x for x in G.all_frame if x!="G.MoreFrame" ] # remove MoreFrame
    # bite change menu 


def ManualCut():
  if G.manual_cut_bool :
    ManualCutClose()

  else : # including no manula_cut_bool 
    G.manual_cut_bool = not G.manual_cut_bool
    G.ManualCutFrame=Frame(G.LeftTopFrame,bg=G.bg[0]) 
    G.all_frame.append("G.ManualCutFrame")
    G.ManualCutFrame.pack(side=TOP,expand=0,fill=X)        

    Label(G.ManualCutFrame,text="Cut image scale",**G.frame_title_arg).pack(side=TOP,anchor="w")

    G.ManualCutGridFrame=Frame(G.ManualCutFrame,bg=G.bg[0])
    G.all_frame.append("G.ManualCutGridFrame")
    G.ManualCutGridFrame.pack(side=TOP,expand=0,fill=X)        

    G.ManualCutGridFrame.columnconfigure(0,weight=1)       
    G.ManualCutGridFrame.columnconfigure(1,weight=1)       

    def GetValue(event):
      dic = {"min_cut":float(G.entries[1].get()),
             "max_cut":float(G.entries[0].get())}
      if W.verbose >2 : print "InitGui.py/ManualCut, dic called , ",dic 
      MG.Scale(dic=dic) # Call MyGui  


    lst = [  ["Max cut","max_cut"],  ["Min cut","min_cut"]  ]
    r=0
    G.entries=[]
    r=0
    for i in lst : 
      G.l=Label(G.ManualCutGridFrame,text=i[0],font=G.font_param,bg=G.bg[0],fg=G.fg[0])
      G.l.grid(row=r,column=0,sticky="snew")#,sticky=W)
      v= StringVar()
      G.e=Entry(G.ManualCutGridFrame, width=10,textvariable=v,font=G.font_param)
      G.e.grid(row=r,column=1,sticky="nsew")#,sticky=W)
      G.e.bind('<Return>',GetValue)
      v.set("%.2e"%G.scale_dic[0][i[1]])
      G.entries.append(v)
      r+=1


    ###############
    ##  CLOSE button
    G.bu_close=Button(G.ManualCutGridFrame,text=u'\u25b4 '+'Close',background=G.bu_close_color,command=ManualCutClose) 
    G.bu_close.grid(row=r,column=0,columnspan=2)         
    if W.verbose >3 : print "Manual Cut called"  
def ManualCutClose():
  G.manual_cut_bool = not G.manual_cut_bool
  G.ManualCutFrame.destroy()      
  G.all_frame = [ x for x in G.all_frame if x!="G.ManualCutFrame" ] # remove Frame

  G.scale_dic[0]["max_cut"] =float(G.entries[0].get())
  G.scale_dic[0]["min_cut"] =float(G.entries[1].get())
  if W.verbose > 3 : print  G.scale_dic[0]["min_cut"]
  if W.verbose > 3 : print  G.scale_dic[0]["max_cut"]
  MG.Scale() 

def TransoformColor(): # made for brighter darker gui bg 
  return   

def BgCl(color=None) :# Background COlor, change the color of ABism take G.bg[0] t
  if color !=None  : G.bg[0] = color 
  def Frames():
    for i in G.all_frame : 
      if not "Paned" in i : 
         if W.verbose > 2 : print i 
         exec(i +"['bg'] = G.bg[0]") in globals(), locals()     # remove 2 first letter because it is G. done for sed , not Paned please 
	 if W.verbose> 9 : print i 
  def Canvas() : # Figure 
    G.fig.set_facecolor(G.bg[0])
    G.fig.canvas.draw() 
    G.figfit.set_facecolor(G.bg[0])
    G.figfit.canvas.draw() 
    G.figresult.set_facecolor(G.bg[0])
    G.figresult.canvas.draw() 
    for i in G.toolbar.winfo_children() : 
       i["bg"] = G.bg[0]
  def MenuBut() : 
    for i in G.MenuBar.winfo_children() : 
       i["bg"] = G.bg[0]
       BackgroundLoop(i) 
  def Rest() :
     BackgroundLoop(G.TextPaned) 

  Frames() ; Canvas() ; MenuBut() ; Rest() 
  return 

def BackgroundLoop(widget): # read G.bg[0], G.fb Colorize all Label and Frame children,  
  #if W.verbose >3 : print "BackgroundLoop :",widget.winfo_class()  
  bolt=    (widget.winfo_class() == "Label")  or (widget.winfo_class()=="Frame") or (widget.winfo_class()=="Menu")  or ( widget.winfo_class() == "Checkbutton") 
  bolt = bolt and ( widget["bg"] !=  G.frame_title_arg["bg"] )  # not change title of frames 
  if bolt :   
    widget["background"] = G.bg[0]
    #if W.verbose >3 : print "I color "
  #elif widget.winfo_class() == "Button" or "Menubutton" : 
  #  widget["background"] = "blue"
    
  for i in widget.winfo_children() :   
     BackgroundLoop(i) 
  return 


def callback(event):
    if W.verbose > 3 : print "clicked at", event.x, event.y , event.widget , event.key 
def TerminalWidget(Frame): # not used 
  import os 
  wid = Frame.winfo_id() 
  #G.c=Button(G.TerminalFrame,text='CLEAR',background= 'cyan',
  #                command =MG.Clear)                    # CLEAR
  #G.c.pack(side=BOTTOM,expand=1,fill=X)
  #os.system('xterm -into %d -geometry 100x150 -sb -e "tty; sh" &' % wid)
  os.system('xterm -into %d -geometry 40x20 &' % wid)

#   def PhotRadius(event):
#      G.phot_type='Aperture',float(v.get().split()[0]),v.get().split()[1]
#      print G.phot_type
#   G.ApertureFrame = Frame(G.PhotFrame)
#   G.ApertureFrame.pack(side=TOP,expand=NO)
#   Label(G.ApertureFrame,text='Aperture Size:').pack(side=LEFT,padx=10,pady=10) 
#   v= StringVar()
#   phot_entry =Entry(G.ApertureFrame, width=10,textvariable=v)
#   phot_entry.pack(side=LEFT,padx=10,pady=10)	
#   v.set('5 FWHM')
#   phot_entry.bind("<Return>",PhotRadius)
#print G.phot_type


def Shortcuts() :  
  #Shortcut, module, function, [  args, kargs  ]
  lst = [["<Control-o>","MG","Open"], 
         ["<Control-q>","MG","Quit"],
         ["<Control-r>","MG","Restart"],
	]


  for i in lst : 
     G.parent.bind_all(    i[0] ,   lambda i=i : vars(i[1])[i[2]]()  ) 



