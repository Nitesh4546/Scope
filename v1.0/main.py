import os
import sys
import shutil
import pyperclip
import subprocess
from time import sleep
from PIL import Image
import customtkinter as ctk
from plyer import notification

#---- Config --
TEMP_IMG = "/tmp/snap.png"

#UI Setup
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

def send_notification(title, msg):
    try:
        notification.notify(
            title=title,
            message=msg,
            app_name="Scope",
            app_icon="./res/icon.png",
            timeout=3
        )
    except Exception as e:
        print(f"Notification failed: {e}")
        pass

    sys.exit(1)

def dependencies_check():
	"""
	Makes sure we have the necessary linux tools installed.
	"""
	reqs = ["slop","maim","tesseract","xclip"]
	not_found = []

	for tool in reqs:
		if not shutil.which(tool):
			not_found.append(tool)

	if not_found:
		msg = f"Missing tools: {','.join(not_found)}\nInstall them."
		title='🚨 MISSING TOOLS 🚨'
		send_notification(title,msg)


def copy_to_clipboard(text):
	try:
		pyperclip.copy(text)
	except:
		title = "🚨 UNABLE TO COPY TEXT TO CLIPBOARD 🚨"
		msg = "Due to some unforseen error the text is not copied to clipboard.Please do it manual selection and copy",
		send_notification(title,msg)


def select_region():
	"""
	Uses slop and maim to select the region on the screen.
	"""
	try:
		#Get region
		p = subprocess.run(['slop','-o','-f','%x,%y,%w,%h'],capture_output=True, text=True)
		if p.returncode !=0:
			return None
		geom = p.stdout.strip()

		if not geom:
			return None

		x,y,w,h = map(int, geom.split(','))

		#get temp img
		subprocess.run(['maim','-g',f"{w}x{h}+{x}+{y}", TEMP_IMG], check=True, stderr=subprocess.DEVNULL)
		return TEMP_IMG

	except Exception:
		return None

def run_ocr(img_path):
	try:
		#Get lang
		p = subprocess.run(['tesseract','--list-langs'],capture_output=True, text=True)
		langs = []
		for l in p.stdout.splitlines()[1:]:
			if l.strip() and l!='osd':
				langs.append(l.strip())

		lang_arg = "+".join(langs) if langs else "eng"

		#OCR
		res = subprocess.run(['tesseract',img_path,'stdout','-l',lang_arg], capture_output=True,text=True)
		return res.stdout.strip()
	except:
		return None



class App(ctk.CTk):
	def __init__(self,start_text=None, img_path=None):
		super().__init__()
		self.img_path = img_path

		self.title("Scope")
		self.geometry("600x500")
		self.overrideredirect(True)
		self.attributes('-alpha',0.92)

		#Colors
		self.col_primary = ("#1a73e8", "#8ab4f8")
		self.col_bg = ("#f1f3f4", "#202124")
		self.col_text = ("#202124", "#e8eaed")
		self.col_red = ("#d93025", "#f28b82")

		#Fonts
		self.f_head = ctk.CTkFont(family="Ronoto", size=22, weight="bold")
		self.f_body = ctk.CTkFont(family="Ronoto", size=14)
		self.f_bold = ctk.CTkFont(family="Ronoto", size=14, weight="bold")
		self.f_small = ctk.CTkFont(family="Ronoto", size=12)

		#Layout
		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)

		#Main Container
		self.main_frame = ctk.CTkFrame(self, corner_radius=12, fg_color=self.col_bg, border_width=2,border_color=self.col_primary)
		self.main_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
		self.main_frame.grid_columnconfigure(0,weight=1)
		self.main_frame.grid_rowconfigure(1,weight=1)

		#Header
		self.head = ctk.CTkFrame(self.main_frame, fg_color="transparent")
		self.head.grid(row=0,column=0,padx=24,pady=(24,12),sticky="ew")
		self.head.grid_columnconfigure(0,weight=1)

		#Title
		self.lbl_title = ctk.CTkLabel(self.head, text="Scope", font=self.f_head, text_color=self.col_text)
		self.lbl_title.grid(row=0,column=0,sticky="w")

		#Controls
		self.ctrls = ctk.CTkFrame(self.head,fg_color="transparent")
		self.ctrls.grid(row=0,column=0,sticky="e")

		#Theme Toogle
		self.sw_theme = ctk.CTkSwitch(
			self.ctrls,
			text="Dark Mode",
			command=self.toggle_theme,
			font=self.f_body,
			text_color=self.col_text,
			onvalue="Dark",
			offvalue="Light"
		)
		self.sw_theme.pack(side="left",padx=(0,15))

		#Init Theme
		if ctk.get_appearance_mode()=="Dark":
			self.sw_theme.select()
		else:
			self.sw_theme.deselect()
		self.setup_drag()

		#Text Area Container
		self.txt_container  =ctk.CTkFrame(self.main_frame, fg_color="transparent")
		self.txt_container.grid(row=1,column=0,padx=24,pady=12,sticky="nsew")
		self.txt_container.grid_rowconfigure(0,weight=1)
		self.txt_container.grid_columnconfigure(0,weight=1)

		#Text Area
		self.txt_area = ctk.CTkTextbox(
			self.txt_container,
			width=500,
			height=300,
			font=self.f_body,
			corner_radius=12,
			border_width=0,
			border_color="black",
			fg_color=("white","#303134"),
			text_color=self.col_text
		)
		self.txt_area.grid(row=0,column=0,sticky="nsew")
		
		# Copy Button
		try:
			self.img_copy = ctk.CTkImage(light_image=Image.open("res/copy.png"),size=(20,20))
		except:
			self.img_copy = None
		self.btn_copy_small = ctk.CTkButton(
			self.txt_container,
			text="" if self.img_copy else "Copy",
			image=self.img_copy,
			width=30,
			height=30,
			command=self.do_copy,
			font=ctk.CTkFont(size=12),
			fg_color="transparent",
			text_color=self.col_text,
			hover_color=("gray80","gray40")
		)
		self.btn_copy_small.place(relx=0.98,rely=0.02,anchor="ne")
		
		# Button
		self.btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
		self.btn_frame.grid(row=2,column=0,padx=24,pady=24,sticky="ew")
		self.btn_frame.grid_columnconfigure(0,weight=1)
		
		# Quit
		self.btn_quit = ctk.CTkButton(
			self.btn_frame,
			text="Quit",
			command=self.quit_app,
			font=self.f_bold,
			fg_color=self.col_red,
			text_color="white",
			corner_radius=20,
			height=40,
			width=80
		)
		self.btn_quit.grid(row=0,column=0,padx=0,pady=0)
		
		#Status
		self.lbl_status = ctk.CTkLabel(self.main_frame,text="Ready",font=ctk.CTkFont(size=12),text_color="gray")
		self.lbl_status.grid(row=3,column=0,padx=24,pady=(0,12),sticky="w")
		
		if start_text:
			self.txt_area.insert("0.0",start_text)
			self.lbl_status.configure(text="Text captured.")
	
	def setup_drag(self):
		for w in [self.main_frame, self.head, self.lbl_title]:
			w.bind("<Button-1>",self.drag_start)
			w.bind("<B1-Motion>",self.drag_move)
	
	def drag_start(self,event):
		self.dx = event.x
		self.dy = event.y
		
	def drag_move(self,event):
		x = self.winfo_x()+(event.x-self.dx)
		y = self.winfo_y()+(event.y-self.dy)
		self.geometry(f"+{x}+{y}")
		
	def toggle_theme(self):
		ctk.set_appearance_mode(self.sw_theme.get())
		
	def quit_app(self):
		self.destroy()
		sys.exit(0)
	
	def do_copy(self):
		txt = self.txt_area.get("0.0","end").strip()
		if txt:
			copy_to_clipboard(txt)
			self.lbl_status.configure(text="Copied!")
			
			# Change button state
			self.btn_copy_small.configure(image=None,text="Copied")
			self.after(3000,self.reset_copy_btn)
			self.after(4000,self.quit_app)
			
			
	def reset_copy_btn(self):
		if self.img_copy:
			self.btn_copy_small.configure(image=self.img_copy,text="")
		else:
			self.btn_copy_small.configure(image=None,text="Copy")

def main():
	dependencies_check()
	
	img = select_region()
	if not img:
		send_notification(title="🚨 UNABLE TO TAKE SCREENSHOT 🚨",msg="Due to some problem the selected region was not saved.")
		return 
	txt = run_ocr(img)
	
	app = App(start_text=txt if txt else "No text found.")
	app.mainloop()

	if os.path(TEMP_IMG):
		try:
			os.remove(TEMP_IMG)
		except OSError as e:
			print("Error removing temp img file")
	
if __name__ == "__main__":
	main()
