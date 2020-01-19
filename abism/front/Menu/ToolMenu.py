"""
    Menu for some other tools (in plugin)
"""
import tkinter as Tk


from abism.plugin.DebugConsole import PythonConsole
from abism.plugin.Histogram import Histopopo

from abism.front import Pick  # to connect PickOne per defautl
from abism.front.util_front import skin


def ToolMenu(root, parent, args):
    """Only function"""
    # pylint: disable=unused-argument
    tool_menu = Tk.Menubutton(parent, **args)
    tool_menu.menu = Tk.Menu(tool_menu, **skin().fg_and_bg)

    lst = [
        ["Profile", lambda: Pick.RefreshPick("profile")],
        ["Stat", lambda: Pick.RefreshPick("stat")],
        ["Histogram", lambda: Histopopo(
            root.FitFrame.get_figure(),
            root.image.sort,
            skin=skin())],
        ["Python Console", PythonConsole],
    ]
    for i in lst:
        tool_menu.menu.add_command(label=i[0], command=i[1])

    tool_menu['menu'] = tool_menu.menu

    return tool_menu
