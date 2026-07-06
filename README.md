# wayscreen_gui
A simple tkinter GUI for screen commands that some wayland users may commonly use, like change screen resolution, refresh rate and brightness.

It's based on `wlr-randr` and `ddcutil`, so if you can't use these, don't use this program.

This program is thought as a replacement for nvidia-settings on X11. It was designed for my own usage and I don't know if it will work properly on other setups.

![example](https://github.com/ObaniGemini/wayscreen_gui/blob/main/example.png)

Dependencies:
- python3
- tkinter
- wlr-randr
- ddcutil
