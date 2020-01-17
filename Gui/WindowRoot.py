"""
    Abism main GUI
"""


# Standard
import sys
import os
from os.path import isfile
import warnings
import threading

# Tkinter
from tkinter import *
from tkinter.filedialog import askopenfilename

# Fancy
from astropy.io import fits
import numpy as np

# Gui
import MenuBar
#from Gui.Menu.MenuBar import MenuBarMaker
from Gui.FrameText import LeftFrame
from Gui.FramePlot import RightFrame

# ArrayFunction
from ArrayFunction.FitsIo import OpenImage


# Variables
from GlobalDefiner import MainVar
import GuyVariables as G
import WorkVariables as W


class RootWindow(Tk):
    """Main window app object
    May one day destroy GuyVariables ...
    Call me like Tk:
        root_window = WindowRoot()
        root_window.mainloop()
    """
    def __init__(self, root_path='.'):
        # Create main app
        super().__init__()

        # Init globals TODO dirty
        G.parent = self
        W.path = root_path
        MainVar()

        # Give title
        self.set_title()
        self.set_icon()

        # Create menu
        MenuBar.MenuBarMaker(self)

        # ALL What is not the menu is a paned windows :
        # I can rezie it with the mouse from left to right,
        # This (all but not the Menu) Frame is called MainPaned
        G.MainPaned = PanedWindow(G.parent, orient=HORIZONTAL, **G.paned_dic)
        G.MainPaned.pack(side=TOP, fill=BOTH, expand=1)

        # 2 LEFT
        G.TextFrame = LeftFrame(G.MainPaned)

        # 3 RIGHT
        G.DrawPaned = RightFrame(G.MainPaned)

        # ######################
        # Init matplotlib figure
        # TODO this should be done as getter
        # Create Image
        G.fig = G.ImageFrame.get_figure()
        G.ImageCanvas = G.ImageFrame.get_canvas()
        G.toolbar = G.ImageFrame.get_toolbar()

        # Create Fit
        G.figfit = G.FitFrame.get_figure()
        G.dpfit = G.FitFrame.get_canvas()

        # Create Result
        G.figresult = G.ResultFrame.get_figure()
        G.dpresult = G.ResultFrame.get_canvas()

        # in case the user launch the program without giving an image as arg
        # TODO remove hardcoded "no_image_name"
        if W.image_name != "no_image_name":
            OpenImage()
            G.ImageFrame.draw_image()



    def set_title(self):
        """Create OS's window title, icon and Set geomrtry"""
        self.title('ABISM (' +
                   "/".join(str(W.image_name).split("/")[-3:]) + ')')

    def set_icon(self):
        """Create OS Icon from resources"""
        if isfile(W.path + '/Icon/bato_chico.gif'):
            bitmap = PhotoImage(file=W.path + '/Icon/bato_chico.gif')
            self.tk.call('wm', 'iconphoto', self._w, bitmap)
        else:
            W.log(3, "->you have no beautiful icon "
                  "because you didn't set the PATH in Abism.py")

    def set_shortcuts(self):
        """TODO not working
        Shortcut, module, function, [  args, kargs  ]
        # Take MG and parents
        """

        for i in [
                ["<Control-o>", "MG", "Open"],
                ["<Control-q>", "G", "Quit"],
                ["<Control-r>", "MG", "Restart"],
                ]:
            self.bind_all(i[0], lambda i=i: vars(i[1])[i[2]]())


def SubstractBackground():
    """Subtract A background image
    Choose a FITS image tho subtract to the current image to get read of the sky
    value or/and the pixel response. This is a VERY basic task that is only
    subtracting 2 images.
    It could be improved but image reduction is not the goal of ABISM
    """
    fp_sky = askopenfilename(
        filetypes=[("fitsfiles", "*.fits"), ("allfiles", "*")])
    W.image_bg_name = fp_sky     # image_background_name
    W.hdulist_bg = fits.open(fp_sky)
    W.Im0_bg = W.hdulist_bg[0].data
    if not W.Im0.shape == W.Im0_bg.shape:
        W.Log(0, 'ERROR : Science image and Background image should have the same shape')
    else:
        W.Im0 -= W.Im0_bg
        InitImage()


def FitType(name):  # strange but works
    """Choose Fit Type
    Different fit types: A Moffat fit is setted by default. You can change it. Gaussian, Moffat,Bessel are three parametrics psf. Gaussian hole is a fit of two Gaussians with the same center by default but you can change that in more option in file button. The Gaussian hole is made for saturated stars. It can be very useful, especially because not may other software utilize this fit.
    Why is the fit type really important? The photometry and the peak of the objects utilize the fit. For the photometry, the fit measure the aperture and the maximum is directly taken from the fit. So changing the fit type can change by 5 to 10% your result
    What should I use? For strehl <10% Gaussian, for Strehl>50% Bessel, between these, Moffat.
    Programmers: Strehl@WindowRoot.py calls SeeingPSF@ImageFunction.py which calls BasicFunction.py
    Todo : fastly analyse the situation and choose a fit type consequently
    """
    W.type["fit"] = name
    G.cu_fit.set(name.replace("2D", ""))  # to change radio but, check
    try:
        if W.aniso_var.get() == 0:
            W.type["fit"] = W.type["fit"].replace('2D', '')
        elif W.aniso_var.get() == 1 and not '2D' in W.type["fit"]:
            W.type["fit"] += '2D'
    except BaseException:
        if W.type["fit"].find('2D') == -1:
            W.type["fit"] += '2D'
    if not W.type["fit"].find('None') == -1:
        W.type["fit"] = 'None'

    # Saturated
    if "Gaussian_hole" in W.type["fit"]:
        try:
            if W.same_center_var.get() == 0:
                W.type["fit"] = W.type["fit"].replace('same_center', '')
                W.log(0, "same_center : We asssume that the saturation",
                      "is centered at the center of th object")
            elif not 'same_center' in W.type["fit"]:
                W.type["fit"] += "same_center"
                W.log(0, "not same_center: We asssume that the saturation",
                      "isn't centered at the center of th object")
        except BaseException:
            if not 'same_center' in W.type["fit"]:
                W.type["fit"] += "same_center"
    W.log(0, 'Fit Type = ' + W.type["fit"])

    # same psf
    if W.same_psf_var.get() == 0:
        W.same_psf = 0
        W.log(0, "same_psf : We will fit the binary with the same psf")
    elif W.same_psf_var.get() == 1:
        W.same_psf = 1
        W.log(0, "not same_psf : We will fit each star with independant psf")

    # change the labels
    #G.fit_type_label["text"] = W.type["fit"]

    return


def Scale(dic={}, load=0, run=""):
    """Cut Image Scale
    Change contrast and color , load if it is loaded with InitImage
    remember that we need to update G.scael_dic in case we opne a new image,
    but this is not really true

    cmap: Image Color
        A menu button will be displayed and in this,
        there is waht is called some radio buttons,
        which permits to select a color for the image.
        And there is at the bottom a button for plotting the contours of objects.
        You have for colors from bright to faint:\n\n"
        ->jet: red,yellow,green,blue\n"
        ->Black&White: White,Black\n"
        ->spectral:red,yellow,green,blue, purple\n"
        ->RdYlBu: blue, white, red\n"
        ->BuPu: purple, white\n"
        ->Contour: This will display the 3 and 5 sigma contours of the objects
            on the image. To delete the contours that may crowd your image,
            just click again on contour.\n"

    fct: Rescale Image Function
        A menu button with some radio button is displayed. Chose the function
        that will transforme the image according to a function. This function
        is apllied to the images values rescaled from 0 to 1 and then the image
        is mutliplied again fit the true min and max cut made.\n\n"
        Programmers, This function is trabsforming G.current_image when the
        true image is stocked under W.Im0 \nIf you want to add some function
        look at the InitGuy.py module, a function with some (2,3,4) thresholds
        (=steps) could be usefull to get stars of (2,3,4) differents color,
        nothing more, one color for each intensity range. This can be done with
        if also.

    scale_cut_type: Cut Image Scale
        A menu button with some radio button is displayed. You need to chose
        the cut for scaling the displaued color of the image (ie: the values of
        the minimum and maximum color). Youhave different way of cutting :\n\n"
        -> None, will take the true max and min values of th image to set the
        displayed color range. Usefull for saturated objects.\n" -> Percentage,
        set the max (min) color as the maximum (minimum) value of the central
        percent% values. For example, 95% reject the 2.5% higher values and
        then take the maximum of the kept values.\n" -> RMS, will take make a
        -1,5 sigma for min and max\n" -> Manual, The power is in your hand, a
        new frame is displayed, enter the min and max value. When satified,
        please close the frame.\n" \n\nProgrammers, a cut setted with the
        histogram can be nice but not so usefull.
    """
    W.log(2, "Scale called with:", dic)

    # RUN THE Stff to change radio button for mac
    if run != "":
        if W.verbose > 3:
            print("Scale, run=", run)
        exec(run, globals())

        #######
        # INIT  WITH CURRENT IMAGE parameters.
    # try :
    if not load:
        G.scale_dic[0]["cmap"] = G.cbar.mappable.get_cmap().name  # Image color
        G.scale_dic[0]["min_cut"] = G.cbar.cbar.norm.vmin  # Image color
        G.scale_dic[0]["max_cut"] = G.cbar.cbar.norm.vmax  # Image color

    ###########
    # CONTOURS
    if("contour" in dic) and not isinstance(dic["contour"], bool):
        if W.verbose > 3:
            print("contour ? ", G.scale_dic[0]["contour"])
        G.scale_dic[0]["contour"] = not G.scale_dic[0]["contour"]
        if G.scale_dic[0]["contour"]:
            if "median" not in G.scale_dic[0]:
                tmp = vars(W.imstat)
            mean, rms = tmp["mean"], tmp["rms"]
            c0, c1, c2, c3, c4, c5 = mean, mean + rms, mean + 2 * \
                rms, mean + 3 * rms, mean + 4 * rms, mean + 5 * rms
            G.contour = G.ax1.contour(W.Im0, (c2, c5),
                                      origin='lower', colors="k",
                                      linewidths=3)
            # extent=(-3,3,-2,2))
            if W.verbose > 0:
                print(
                    "---> Contour of 3 and 5 sigma, clik again on contour to delete its.")

        else:  # include no contour  delete the contours
            if not load:
                for coll in G.contour.collections:
                    G.ax1.collections.remove(coll)

    ############
    # UPDATE UPDATE
    if W.verbose > 2:
        print(" MG.scale ,Scale_dic ", G.scale_dic[0])
    dic["contour"] = G.scale_dic[0]["contour"]
    G.scale_dic[0].update(dic)  # UPDATE DIC

    ###########
    # CUT
    if "scale_cut_type" in dic:
        if dic["scale_cut_type"] == "None":
            # IG.ManualCut()
            G.scale_dic[0]["min_cut"] = W.imstat.min
            G.scale_dic[0]["max_cut"] = W.imstat.max
        else:
            import Scale  # otherwise get in conflict with Tkinter
            dictmp = {"whole_image": "useless"}
            dictmp.update(G.scale_dic[0])
            tmp = Scale.MinMaxCut(W.Im0, dic=dictmp)
            G.scale_dic[0]["min_cut"] = tmp["min_cut"]
            G.scale_dic[0]["max_cut"] = tmp["max_cut"]
        if W.verbose > 2:
            "I called Scale cut "

    ######
    # SCALE FCT
    if "stretch" not in G.scale_dic[0]:  # in case
        G.scale_dic[0]["stretch"] = "linear"

    ###############
    #  RELOAD THE IMAGE
    if not load:
        Draw()

     ##########
     # RELOAD PlotStar
        try:
            PlotStar2()
        except BaseException:
            pass  # in case you didn't pick the star yet
    return


def FigurePlot(x, y, dic={}):
    """ x and y can be simple list
    or also its can be list of list for a multiple axes
    dic : title:"string", logx:bol, logy:bol, xlabel:"" , ylabel:""
    """
    #from matplotlib import pyplot as plt
    W.log(3, "MG.FigurePlotCalled")
    from matplotlib import pyplot as plt  # necessary if we are in a sub process
    default_dic = {"warning": 0, "title": "no-title"}
    default_dic.update(dic)
    dic = default_dic

    def SubPlot(x, y):
        nx, ny = 7, 5
        if "logx" in dic:
            ax.set_xscale("log")
        if "logy" in dic:
            ax.set_yscale("log")
        if "xlabel" in dic:
            ax.set_xlabel(dic["xlabel"])
        if "ylabel" in dic:
            ax.set_ylabel(dic["ylabel"])

        ax.plot(x, y)

        ax2 = ax.twiny()
        ax2.set_xticks(np.arange(nx))
        xlist = np.linspace(0, x[-1] * W.head.pixel_scale, nx)
        xlist = [int(1000 * u) for u in xlist]
        ax2.set_xticklabels(xlist, rotation=45)
        ax2.set_xlabel(u"Distance [mas]")

        ax3 = ax.twinx()
        ax3.set_yticks(np.arange(ny))
        ylist = np.linspace(0, y[0], ny)
        ylist = [int(u) for u in ylist]
        ax3.set_yticklabels(ylist)
        ax3.set_ylabel(u"number count per pixel")
        ############
        # TWIN axes

    W.log(3, 50 * '_', "\n", threading.currentThread().getName(),
          "Starting------------------\n")

    global ax
    G.contrast_fig.clf()
    # tfig.canvas.set_window_title(dic["title"])

    if not isinstance(x[0], list):  # otherwise multiple axes
        W.log(3, "MG.FigurePlot, we make a single plot")
        ax = G.contrast_fig.add_subplot(111)
        #from mpl_toolkits.axes_grid1 import host_subplot
        #ax = host_subplot(111)
        SubPlot(x, y)
        if not dic["warning"]:
            warnings.simplefilter("ignore")
        W.log(3, "I will show ")
        G.contrast_fig.canvas.draw()
        if not dic["warning"]:
            warnings.simplefilter("default")
        # tfig.show()

    # Over
    W.log(3, '_' * 50 + "\n",
          threading.currentThread().getName(),
          'Exiting' + 20 * '-' + "\n")