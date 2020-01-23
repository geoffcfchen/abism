"""
    The Tkinter Frame using matplotlib
    TODO stop putting all in G
"""
import re

# Module
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas, \
    NavigationToolbar2Tk
from numpy import sqrt, float32

# Front
from abism.front.matplotlib_extension import DraggableColorbar, MyNormalize, zoom_handler
from abism.front.util_front import photo_up, photo_down, skin, TitleLabel, \
    set_figure_skin
import abism.front.util_front as G

# TODO must be remooved
from abism.front import Pick
from abism.front.AnswerReturn import PlotStar2
# TODO this should not be here

# Back
from abism.back.ImageFunction import PixelMax
import abism.back.util_back as W

from abism.util import log, get_root, get_state

class PlotFrame(tk.Frame):
    """Frame with a mpl figure"""
    def __init__(self, parent):
        super().__init__(parent, skin().frame_dic)

        # Grid stuff
        self.rowconfigure(0, weight=100)
        self.rowconfigure(1, weight=1)  # not resize the toolbar
        self.columnconfigure(0, weight=1)  # not resize the toolbar

        # Helper auto add (can get confusing)
        parent.add(self)

        self._fig = None  # Figure
        self._arrow = None  # Button
        # At bottom
        self._toolbar_frame = None  # Container for toolbar
        self._toolbar = None
        self._canvas = None
        # See toolbar by default cause it is grided
        #   And in case no hide button, I see it (cf: Image)
        self._see_toolbar = True
        self._cbar = None  # ColorBar

    def init_canvas(self, fig):
        """Init canvas && Init toolbar inside
        Canvas requires _fig
        Toolbar requires canvas
        """
        # Figure
        fig.set_facecolor(skin().color.bg)

        self._canvas = FigureCanvas(fig, master=self)
        self._canvas.get_tk_widget()['bg'] = skin().color.bg
        # No borders: used to locate focus
        self._canvas.get_tk_widget()["highlightthickness"] = 0
        self._canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # TOOLBAR
        self._toolbar_frame = tk.Frame(self, **skin().frame_dic)
        self._toolbar_frame.grid(row=1, column=0, sticky="nsew")
        self._toolbar = NavigationToolbar2Tk(self._canvas, self._toolbar_frame)
        self._toolbar["bg"] = skin().color.bg
        for i in self._toolbar.winfo_children():
            i["bg"] = skin().color.bg
        self._toolbar.grid(row=0, column=0, sticky="nsew")

    def init_label(self, s_label):
        """Create label bottom left"""
        TitleLabel(self, text=s_label).place(x=0, y=0)

    def init_toolbar_button(self):
        """Create toolbar button"""
        self._arrow = tk.Button(
            self, command=self.toogle_toolbar, image=photo_up(), **skin().button_dic)
        self._arrow.place(relx=1., rely=1., anchor="se")
        self.toogle_toolbar()

    def toogle_toolbar(self):
        """Toogle toolbar visibility"""
        self._see_toolbar = not self._see_toolbar

        # CREATE
        if self._see_toolbar:
            log(3, "Showing toolbar")
            self._arrow.configure(image=photo_down())
            self._toolbar_frame.grid(row=1, column=0, sticky="nsew")

        # DESTROY
        else:
            log(3, "Hidding toolbar")
            self._arrow.configure(image=photo_up())
            self._toolbar_frame.grid_forget()

    def get_figure(self):
        """Return the figure for a direct matplotlib use
        You should avoid that
        """
        return self._fig

    def get_canvas(self):
        """Getter for global"""
        return self._canvas

    def get_toolbar(self):
        """Getter for global"""
        return self._toolbar

    def is_toolbar_active(self):
        return self._toolbar._active in ('PAN', 'ZOOM')

    def redraw(self):
        self._fig.canvas.draw()

    def update_skin(self):
        """Update skin, appearance"""
        # Update parameters
        set_figure_skin(self._fig, skin())
        self.redraw()

    def reset_figure_ax(
            self,
            format_coord=lambda x, y: '',
            xlabel='', ylabel='',
    ):
        """Reset figure, return ax
        format_coord: fct x,y -> format
        """
        self._fig.clf()
        ax = self._fig.add_subplot(111)
        ax.format_coord = format_coord
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        return ax


class ImageFrame(PlotFrame):
    """Frame with science image"""
    def __init__(self, parent):
        super().__init__(parent)
        # Keep contours to remove them
        self.contours = None

        # Create figure && Adjust size and color
        self._fig = Figure()
        self._fig.subplots_adjust(left=0.07, right=0.93, top=0.95, bottom=0.05)

        # Label && Canvas
        self.init_label("Image")
        self.init_canvas(self._fig)


    def extend_matplotlib(self):
        """Enable scroll with mouse"""
        # Scroll
        def zoom_handler_wrapper(event):
            zoom_handler(event, self._fig.axes[0],
                         self._fig.canvas.draw, base_scale=1.2)

        self._fig.canvas.mpl_connect('scroll_event', zoom_handler_wrapper)


    def draw_image(self, new_fits=True):
        """Init image
        From Work variable
        """
        # Reset
        try:
            self._cbar.disconnect()
            del self._cbar
            self._fig.clf()
        except BaseException:
            log(5, 'InitImage, cannot delete cbar')

        # Create axes
        ax = self._fig.add_subplot(111)

        # Get image arry
        im0 = get_root().image.im0.astype(float32)

        # Display
        drawing = ax.imshow(
            im0,
            vmin=get_state().i_image_min_cut,
            vmax=get_state().i_image_max_cut,
            cmap=get_state().s_image_color_map,
            # orgin=lower to get low y down
            origin='lower')

        # Compass
        try:
            self.RemoveCompass()
        except BaseException:
            pass
        self.DrawCompass()

        # ColorBar && TooBar
        self._toolbar.update()
        self._cbar = self._fig.colorbar(drawing, pad=0.02)
        # TODO not here :
        G.cbar = self._cbar
        self._cbar = DraggableColorbar(self._cbar, drawing, self.Draw)
        self._cbar.connect()

        # Image levels
        def z(x, y):
            try:
                res = im0[y, x]
            except IndexError:
                res = 0
            return res

        def z_max(x, y):
            return PixelMax(im0, r=(y - 10, y + 11, x - 10, x + 11))[1]

        def format_coordinate(x, y):
            x, y = int(x), int(y)
            return "zmax=%5d, z=%5d, x=%4d, y=%4d" % (z_max(x, y), z(x, y), x, y)

        # Head up display
        ax.format_coord = format_coordinate

        self.CutImageScale()

        # TODO
        # CutIamgeScale is drawing, so rename with some update, refresh
        # Draw
        #self._fig.canvas.draw()

        #####################
        ###  SOME  CLICKS #
        #####################
        # TODO move me ::
        Pick.RefreshPick("one")  # assuming that the default PIck is setted yet

        # I don't know why I need to pu that at the end but it worls like that
        # # does not work it put in Science Variables
        if new_fits:
            get_root().LabelFrame.update_label()

        self.extend_matplotlib()


    def add_contour(self):
        tmp = get_root().image.get_stat_as_dic()
        mean, rms = tmp["mean"], tmp["rms"]
        c0, c1, c2, c3, c4, c5 = mean, mean + rms, mean + 2 * \
            rms, mean + 3 * rms, mean + 4 * rms, mean + 5 * rms

        im0 = get_root().image.im0.astype(float32)
        self.contours = self._fig.axes[0].contour(
            im0, (c2, c5),
            origin='lower', colors="k",
            linewidths=3)

        # extent=(-3,3,-2,2))
        log(0, "---> Contour of 3 and 5 sigma, "
            "clik again on contour to delete its.")

    def remove_contour(self):
        if self.contours is None: return
        for coll in self.contours.collections:
            coll.remove()
        self.contours = None

    def CutImageScale(self):
        """Change contrast and color
        """
        log(5, 'CutImage Scale called')

        ###########
        # CONTOURS
        log(3, "contour ? ", get_state().b_image_contour)
        self.remove_contour()
        if get_state().b_image_contour:
            self.add_contour()


        ###########
        # CUT
        if get_state().s_image_stretch == "None":
            # IG.ManualCut()
            get_state().i_image_min_cut = get_root().image.stat.min
            get_state().i_image_max_cut = get_root().image.stat.max
        else:
            i_min, i_max = get_root().image.MinMaxCut()
            get_state().i_image_min_cut = i_min
            get_state().i_image_max_cut = i_max


        # Reload
        self.Draw()
        try:
            # in case you didn't pick the star yet
            PlotStar2()
        except BaseException:
            pass


    def Draw(self):
        """ Redraw image with new scale"""

        cmap = get_state().s_image_color_map
        i_min, i_max = get_state().i_image_min_cut, get_state().i_image_max_cut

        # Normalize
        mynorm = MyNormalize(
            vmin=i_min, vmax=i_max,
            vmid=i_min-5,
            stretch=get_state().s_image_stretch)

        self._cbar.mappable.set_cmap(cmap)
        self._cbar.mappable.set_norm(mynorm)

        self._cbar.cbar.patch.figure.canvas.draw()
        self.redraw()

        # Try to draw  result frame
        try:
            for ax in get_root().ResultFrame.get_figure().axes:
                if not len(ax.images): continue
                mappable = ax.images[0]
                mappable.set_norm(mynorm)
                mappable.set_cmap(cmap)
            get_root().ResultFrame.redraw()
        except BaseException as e:
            log(2, "Draw cannot draw in Result Figure (bottom right):", e)


    def RemoveCompass(self):
        ax = self._fig.axes[0]
        ax.texts.remove(G.north)
        ax.texts.remove(G.east)
        ax.texts.remove(G.north_text)
        ax.texts.remove(G.east_text)


    def DrawCompass(self):
        """Draw WCS compass to see 'north'"""
        ax = self._fig.axes[0]
        im0 = get_root().image.im0.astype(float32)

        if not (("CD1_1" in vars(get_root().header)) and ("CD2_2" in vars(get_root().header))):
            log(0, "WARNING WCS Matrix not detected,",
                "I don't know where the north is")
            get_root().header.CD1_1 = get_root().header.pixel_scale * 3600
            get_root().header.CD2_2 = get_root().header.pixel_scale * 3600

        if not (("CD1_2" in vars(get_root().header)) and ("CD2_1" in vars(get_root().header))):
            get_root().header.CD1_2, get_root().header.CD2_1 = 0, 0

        north_direction = [-get_root().header.CD1_2, -get_root().header.CD1_1] / \
            sqrt(get_root().header.CD1_1**2 + get_root().header.CD1_2**2)
        east_direction = [-get_root().header.CD2_2, -get_root().header.CD2_1] / \
            sqrt(get_root().header.CD2_1**2 + get_root().header.CD2_2**2)

        # CALCULATE ARROW SIZE
        coord_type = "axes fraction"
        if coord_type == "axes fraction":    # for the arrow in the image, axes fraction
            arrow_center = [0.95, 0.1]  # in figura fraction
            # -  because y is upside down       think raw collumn
            north_point = arrow_center + north_direction / 10
            east_point = arrow_center + east_direction / 15

        # for the arrow IN the image coords can be "data" or "figure fraction"
        elif coord_type == "data":
            # in figure fraction
            arrow_center = [0.945 * len(im0), 0.1 * len(im0)]
            # -  because y is upside down       think raw collumn
            north_point = [arrow_center + north_direction / 20 * len(im0),
                           arrow_center - north_direction / 20 * len(im0)]
            east_point = [north_point[1] + east_direction / 20 * len(im0),
                          north_point[1]]
        W.north_direction = north_direction
        W.east_direction = east_direction
        log(3, "north", north_point, east_point,
            arrow_center, north_direction, east_direction)

        #################
        # 2/ DRAW        0 is the end of the arrow
        if get_root().header.wcs is not None:
            G.north = ax.annotate(
                "",
                # we invert to get the text at the end of the arrwo
                xy=arrow_center, xycoords=coord_type,
                xytext=north_point, textcoords=coord_type, color="purple",
                arrowprops=dict(
                    arrowstyle="<-", facecolor="purple", edgecolor="purple"),
                # connectionstyle="arc3"),
                )
            G.east = ax.annotate(
                "",
                xy=arrow_center, xycoords=coord_type,
                xytext=east_point, textcoords=coord_type, color="red",
                arrowprops=dict(
                    arrowstyle="<-", facecolor='red', edgecolor='red'),
                # connectionstyle="arc3"),
                )
            G.north_text = ax.annotate(
                'N', xytext=north_point,
                xy=north_point, textcoords=coord_type, color='purple')
            G.east_text = ax.annotate(
                'E', xytext=east_point,
                xy=east_point, textcoords=coord_type, color='red')


    def Cube(self):
        """Prepare Cube buttons"""
        # Try to destroy if not a cube
        if not get_root().image.is_cube:
            try:
                G.CubeFrame.destroy()
            except BaseException:
                pass
        # Create a cube interface else
        else:
            # FRAME
            G.CubeFrame = tk.Frame(G.ButtonFrame, **skin().frame_dic)
            G.CubeFrame.pack(side=tk.TOP, expand=0, fill=tk.X)

            # CUBE IMAGE SELECTION
            # LEFT
            G.bu_cubel = tk.Button(G.CubeFrame, text='<-',
                                command=lambda: self.CubeDisplay("-"), **skin().button_dic)

            # ENTRY
            G.cube_var = tk.StringVar()
            G.cube_entry = tk.Entry(
                G.CubeFrame, width=10, justify=tk.CENTER,
                textvariable=G.cube_var, bd=0, **skin().fg_and_bg)
            G.cube_var.set(get_root().image.cube_num + 1)
            G.cube_entry.bind("<Return>", lambda x: self.CubeDisplay("0"))

            # RIGHT
            G.bu_cuber = tk.Button(
                G.CubeFrame, text='->',
                command=lambda: self.CubeDisplay("+"), **skin().button_dic)

            # GRID
            for i in range(3):
                G.CubeFrame.columnconfigure(i, weight=1)
            lt = TitleLabel(G.CubeFrame, text="Cube Number")
            lt.grid(row=0, column=0, columnspan=3, sticky="w")
            G.bu_cubel.grid(row=1, column=0, sticky="nsew")
            G.cube_entry.grid(row=1, column=1, sticky="nsew")
            G.bu_cuber.grid(row=1, column=2, sticky="nsew")


    def CubeDisplay(self, stg_click):
        """Callback for cube button + -"""
        if stg_click == '+':
            get_root().image.cube_num += 1
        elif stg_click == '-':
            get_root().image.cube_num -= 1
        elif stg_click == '0':
            get_root().image.cube_num = float(G.cube_var.get())

        G.cube_var.set(get_root().image.cube_num + 1)
        self.draw_image(new_fits=False)


class FitFrame(PlotFrame):
    """Frame with the curve of the fit (1d)"""
    def __init__(self, parent):
        super().__init__(parent)

        # Create figure && Adjust size and color
        self._fig = Figure(figsize=(5, 2.5))
        self._fig.subplots_adjust(left=0.15, right=0.9, top=0.9, bottom=0.2)

        # Label && Canvas
        self.init_label("Photometric Profile")
        self.init_canvas(self._fig)
        self.init_toolbar_button()


class ResultFrame(PlotFrame):
    """Frame with some results, dependant on operation"""
    def __init__(self, parent):
        super().__init__(parent)

        # Create figure && Adjust size and color
        self._fig = Figure(figsize=(3, 2.5))
        self._fig.subplots_adjust(left=0.1, right=0.9, top=1.05, bottom=-0.15)

        # Label && Canvas
        self.init_label("2D Shape")
        self.init_canvas(self._fig)
        self.init_toolbar_button()


class RightFrame(tk.PanedWindow):
    """Full Container"""
    def __init__(self, root, parent):
        # Append self, vertically splited
        super().__init__(parent, orient=tk.VERTICAL, **skin().paned_dic)
        parent.add(self)

        # Add science image frame
        root.ImageFrame = ImageFrame(self)

        # Append bottom, horizontally splitted container of 2 frames
        G.RightBottomPaned = tk.PanedWindow(
            self, orient=tk.HORIZONTAL, **skin().paned_dic)
        self.add(G.RightBottomPaned)

        # Add Fit (bottom left)
        root.FitFrame = FitFrame(G.RightBottomPaned)

        # Add Result (bottom right)
        root.ResultFrame = ResultFrame(G.RightBottomPaned)