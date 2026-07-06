#!/bin/python

import tkinter as tk
import json
from tkinter import ttk
import subprocess


class ComboBox:
	def __init__(self, root, name, cb, width):
		self.frame = ttk.Frame(root)

		self.name = tk.Label(self.frame, text=name, width=width)
		self.node = ttk.Combobox(self.frame)
		self.node.bind('<<ComboboxSelected>>', cb)

		self.name.pack(side="left")
		self.node.pack()



class Slider:
	def __init__(self, root, name, maxi, current, code, width):
		self.frame = ttk.Frame(root)
		self.name = tk.Label(self.frame, text=name, width=width)
		self.node = ttk.Scale(self.frame, from_=0, to=maxi, orient='horizontal', command=self.update_label)
		self.value = tk.Label(self.frame, text=str(current), width=3)

		self.node.set(current)
		self.code = code
		self.previous = self.node.get()

		self.name.pack(side="left")
		self.node.pack(side="left")
		self.value.pack()

	def update_label(self, _r1 = None):
		self.value['text'] = str(int(self.node.get()))
		



def cmd_get(p):
	return subprocess.Popen(p, shell=True, stdout=subprocess.PIPE).stdout.read().decode(encoding="utf-8")

def cmd_call(p):
	subprocess.call(p, shell=True)




screens = {}
currents = {}





def get_screens():
	global screens
	return list(screens.keys())

def get_res(screen):
	global screens
	return list(screens[screen].keys())

def get_rate(screen, res):
	global screens
	return list(screens[screen][res])





def update_scr(_r = None):
	global scr_combo
	global res_combo
	global rate_combo

	selected = scr_combo.node.get()
	res_combo.node['values'] = get_res(selected)
	res_combo.node.set(currents[selected][0])
	update_res()
	rate_combo.node.set(currents[selected][1])


def update_res(_r = None):
	global scr_combo
	global res_combo
	global rate_combo
	
	if res_combo.node.get() not in res_combo.node['values']:
		res_combo.node.set(res_combo.node['values'][0])

	rate_combo.node['values'] = get_rate(scr_combo.node.get(), res_combo.node.get())
	update_rate()

def update_rate(_r = None):
	global rate_combo

	if rate_combo.node.get() not in rate_combo.node['values']:
		rate_combo.node.set(rate_combo.node['values'][0])
	print(rate_combo.node.get())







def update_info():
	global screens
	global currents
	global scr_combo

	screen_info = json.loads(cmd_get("wlr-randr --json"))

	screens = {}
	currents = {}
	
	for screen in screen_info:
		name = screen['name']

		screens[name] = {}
		for mode in screen['modes']:
			res = str(mode['width']) + 'x' + str(mode['height'])
			rate = str(mode['refresh'])

			if res not in screens[name]:
				screens[name][res] = set()
			screens[name][res].add(rate)

			if mode['current']:
				currents[name] = (res, rate)

	scr_combo.node['values'] = get_screens()
	scr_combo.node.set(get_screens()[0])
	update_scr()



sliders = {}

def update_color_options(root):
	def get_field(field, names):
		for name in names:
			if name in field:
				return name
		return ""

	global sliders
	lines = cmd_get("ddcutil getvcp color").split('\n')

	for line in lines:
		fields = line.split("):")
		code = fields[0][9:13]

		name = get_field(fields[0], ["Brightness", "Contrast", "Video black level: Red", "Video black level: Green", "Video black level: Blue"])
		if name != "":
			values = fields[1].split(', ')
			current = 0
			maxi = 0

			for value in values:
				field = value.split(' = ')
				if "current value" in field[0]:
					current = int(field[1])
				elif "max value" in field[0]:
					maxi = int(field[1])

			sliders[name] = Slider(root, name, maxi, current, code, 20)



def set_res():
	global scr_combo
	global res_combo
	global rate_combo
	global sliders

	cmd_call("wlr-randr --output " + scr_combo.node.get() + " --mode " + res_combo.node.get() + "@" + rate_combo.node.get())

	for key in sliders.keys():
		curr = sliders[key].node.get()
		if sliders[key].previous != curr:
			cmd_call("ddcutil setvcp " + sliders[key].code + " " + str(int(curr)))
			sliders[key].previous = curr







root = tk.Tk()
root.title("Screen settings")

message = tk.Label(root, text="Select your resolution")
message.pack()

scr_combo = ComboBox(root, "Screen", update_scr, 20)
res_combo = ComboBox(root, "Resolution", update_res, 20)
rate_combo = ComboBox(root, "Refresh Rate", update_rate, 20)


apply_btn = tk.Button(root, text="Apply", command=set_res)
reload_btn = tk.Button(root, text="Refresh", command=update_info)



scr_combo.frame.pack()
res_combo.frame.pack()
rate_combo.frame.pack()

update_color_options(root)
for slider in sliders.values():
	slider.frame.pack()

apply_btn.pack()
reload_btn.pack()

update_info()

root.mainloop()