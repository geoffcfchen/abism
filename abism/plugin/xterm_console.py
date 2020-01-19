"""
-l  log
-lc unicode
-lf +file descriptor: to log to file
-sb scrollback ability on
-c  +command: send command (just spawn, no exec like -e)
"""
import tkinter as tk
import subprocess as sp
from re import match
from threading import Thread
from queue import Queue


def main():
    # Init
    root = tk.Tk()
    queue = Queue()

    # Pack main frame
    termf = tk.Frame(root, width=800, height=800)
    termf.pack(fill=tk.BOTH, expand=tk.YES, padx=0, pady=0)
    wid = termf.winfo_id()

    # Allow window resize
    sp.Popen("""echo '*VT100.allowWindowOps: true' | xrdb -merge""", shell=True)

    # Craft command
    cmd = (
        # Create into me
        f'xterm -into {wid} -geometry 100x50 '
        # Log to stdout
        r'-sb -l -lc -lf /dev/stdout '
        # Launch `ps` command: output, tty, = for remove header
        """-e /bin/bash -c "ps -o tt=;bash" """
        r'| tee'
    )
    print('Launching:', cmd)

    # Spawn Xterm
    process = sp.Popen(
        cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    print('Xterm pid:', process.pid)

    # Get pts
    thread = Thread(target=lambda: get_xterm_pts(termf, process, queue))
    thread.start()

    # Set resize callback
    termf.bind("<Configure>", lambda event: on_resize(event, queue))

    # Start
    root.mainloop()


def on_resize(event, queue):
    """On resize: send escape sequence to pts"""
    # Magic && Check
    magic_x, magic_y = 6.1, 13
    print('Resize (w, h):', event.width, event.height)
    if not queue.queue: return

    # Calculate
    width = int(event.width / magic_x)
    height = int(event.height / magic_y)
    print('To (lin,col):', height, width)
    ctl = f"\u001b[8;{height};{width}t"

    # Send to pts
    with open(queue.queue[0], 'w') as f:
        f.write(ctl)


def get_xterm_pts(parent, process, queue):
    """Retrieve pts(`process`) -> `queue`"""
    while True:
        out = process.stdout.readline().decode()
        print('Xterm out' + out)

        match_pts = match(r'pts/\d+', out)
        if match_pts:
            pts = '/dev/' + match_pts.group(0)
            print('-----------> pts:', pts)
            queue.put(pts)
            break

        if out == b'' and process.poll() is not None:
            break

    # Resize now
    fake_event = tk.Event()
    fake_event.width = parent.winfo_width()
    fake_event.height = parent.winfo_height()
    on_resize(fake_event, queue)


if __name__ == '__main__':
    main()
