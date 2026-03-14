import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageOps
import cv2
import numpy as np

class AdvancedImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Image Processing Suite")
        self.root.geometry("1100x800")
        self.root.configure(bg="#121212")
        
        # إدارة البيانات
        self.original_img = None
        self.current_img = None
        self.history = [] # لدعم خاصية الـ Undo
        
        self.create_modern_ui()
        self.create_default_canvas_msg()

    def create_modern_ui(self):
        # --- الشريط العلوي (Top Bar) ---
        top_bar = tk.Frame(self.root, bg="#800B1F", height=70)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)
        
        # العنوان (كما طلبت دون تغيير)
        title = tk.Label(top_bar, text="✨ Advanced Image Editor ✨", 
                        font=("Segoe UI", 20, "bold"),
                        bg="#800B1F", fg="white")
        title.pack(side="left", padx=25, pady=10)

        # أزرار التحكم في الملفات
        btn_style = {"font": ("Tahoma", 11, "bold"), "bd": 0, "padx": 20, "pady": 8, "cursor": "hand2"}
        
        tk.Button(top_bar, text="Open Image", command=self.open_image,
                  bg="#181415", fg="white", **btn_style).pack(side="left", padx=10)
        
        tk.Button(top_bar, text="Save Result", command=self.save,
                  bg="#B3304D", fg="white", **btn_style).pack(side="left", padx=5)

        tk.Button(top_bar, text="Undo ↩", command=self.undo,
                  bg="#444", fg="white", **btn_style).pack(side="right", padx=20)

        # --- الحاوية الرئيسية ---
        main_container = tk.Frame(self.root, bg="#121212")
        main_container.pack(fill="both", expand=True)

        # منطقة عرض الصورة (Canvas)
        self.image_frame = tk.Frame(main_container, bg="#121212")
        self.image_frame.pack(side="left", fill="both", expand=True)
        
        self.image_canvas = tk.Canvas(self.image_frame, bg="#181415", highlightthickness=1, highlightbackground="#333")
        self.image_canvas.pack(expand=True, fill="both", padx=40, pady=40)

        # --- القائمة الجانبية المتحركة (Sidebar with Scrolling) ---
        right_panel = tk.Frame(main_container, bg="#181415", width=340)
        right_panel.pack(side="right", fill="y")
        right_panel.pack_propagate(False)

        # السكرول بار للقائمة
        self.sidebar_canvas = tk.Canvas(right_panel, bg="#181415", highlightthickness=0, width=320)
        scrollbar = tk.Scrollbar(right_panel, orient="vertical", command=self.sidebar_canvas.yview)
        self.sidebar_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.sidebar_inner = tk.Frame(self.sidebar_canvas, bg="#181415")
        self.sidebar_canvas.create_window((0,0), window=self.sidebar_inner, anchor="nw", width=320)
        
        self.sidebar_inner.bind("<Configure>", lambda e: self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all")))
        self.sidebar_canvas.configure(yscrollcommand=scrollbar.set)
        
        # إضافة تصنيفات الفلاتر
        self.create_control_panel(self.sidebar_inner)

    def create_control_panel(self, parent):
        # نفس الفلاتر التي طلبتها تماماً باللغة الإنجليزية
        self.create_category(parent, "🎨 COLOR FILTERS", [
            ("Grayscale", self.filter_grayscale),
            ("Sepia", self.filter_sepia),
            ("RGB Shift", self.filter_rgb_shift),
            ("Posterize", self.filter_posterize),
            ("Solarize", self.filter_solarize),
        ])
        self.create_category(parent, "🔧 QUICK ADJUSTMENTS", [
            ("Brightness", self.adj_brightness),
            ("Contrast", self.adj_contrast),
            ("Saturation", self.adj_saturation),
            ("Hue Shift", self.adj_hue),
        ])
        self.create_category(parent, "🌊 BLUR & EFFECTS", [
            ("Gaussian Blur", self.effect_gaussian_blur),
            ("Pixelize", self.effect_pixelize),
            ("Edge Enhance", self.effect_oil_paint),
        ])
        self.create_category(parent, "⚡ EDGE DETECT", [
            ("Canny", self.edge_canny),
            ("Sobel", self.edge_sobel),
            ("Laplacian", self.edge_laplacian),
            ("Contours", self.edge_contours),
        ])
        self.create_category(parent, "🔄 TRANSFORM", [
            ("Rotate 90°", self.transform_rotate90),
            ("Flip Horizontal", self.transform_flip_h),
            ("Flip Vertical", self.transform_flip_v),
            ("Mirror", self.transform_mirror),
        ])

    def create_category(self, parent, title, buttons):
        tk.Label(parent, text=title, font=("Calibri", 13, "bold"),
                 bg="#B3304D", fg="white", pady=10).pack(fill="x", pady=(15, 2))
        
        btn_frame = tk.Frame(parent, bg="#181415")
        btn_frame.pack(fill="x", padx=10)
        
        for btn_text, cmd in buttons:
            btn = tk.Button(btn_frame, text=btn_text, command=cmd,
                            bg="#252122", fg="#DDD", font=("Calibri", 12),
                            bd=0, height=2, cursor="hand2", activebackground="#800B1F", activeforeground="white")
            btn.pack(fill="x", pady=2)
            # تأثير Hover
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#353132"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#252122"))

    # --- إدارة الصور والعرض ---
    def open_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.original_img = Image.open(file_path).convert('RGB')
            self.current_img = self.original_img.copy()
            self.history = [self.current_img.copy()]
            self.display_image(self.current_img)

    def display_image(self, pil_img):
        self.root.update()
        w, h = self.image_canvas.winfo_width(), self.image_canvas.winfo_height()
        
        disp_img = pil_img.copy()
        disp_img.thumbnail((w-60, h-60), Image.Resampling.LANCZOS)
        
        self.photo = ImageTk.PhotoImage(disp_img)
        self.image_canvas.delete("all")
        self.image_canvas.create_image(w//2, h//2, image=self.photo, anchor="center")

    def create_default_canvas_msg(self):
        self.root.update()
        self.image_canvas.create_text(self.image_canvas.winfo_width()//2, 
                                      self.image_canvas.winfo_height()//2, 
                                      text="Welcome! Please Open an Image", fill="#555", font=("Arial", 14))

    def undo(self):
        if len(self.history) > 1:
            self.history.pop()
            self.current_img = self.history[-1].copy()
            self.display_image(self.current_img)
        else:
            messagebox.showinfo("Undo", "Already at the original state.")

    # --- النافذة المنبثقة (Popup System) كما طلبت ---
    def show_effect_in_window(self, img, title="Effect Preview"):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.configure(bg="#181415")
        
        preview = img.copy()
        preview.thumbnail((500, 500))
        img_tk = ImageTk.PhotoImage(preview)
        
        lbl = tk.Label(win, image=img_tk, bg="#181415")
        lbl.image = img_tk
        lbl.pack(padx=25, pady=25)
        
        btn_f = tk.Frame(win, bg="#181415")
        btn_f.pack(pady=15)
        
        tk.Button(btn_f, text="Apply Effect", bg="#B3304D", fg="white", padx=25, pady=8, bd=0,
                  command=lambda: [self.apply_confirm(img), win.destroy()]).pack(side="left", padx=10)
        tk.Button(btn_f, text="Discard", bg="#444", fg="white", padx=25, pady=8, bd=0,
                  command=win.destroy).pack(side="left")

    def apply_confirm(self, img):
        self.current_img = img.copy()
        self.history.append(self.current_img.copy())
        self.display_image(self.current_img)

    def save(self):
        if self.current_img:
            path = filedialog.asksaveasfilename(defaultextension=".jpg")
            if path: self.current_img.save(path)

    # --- تحويلات OpenCV ---
    def pil_to_cv2(self, pil_img): return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    def cv2_to_pil(self, cv_img): return Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))

    # --- الفلاتر (نفس القائمة تماماً) ---
    def filter_grayscale(self): self.show_effect_in_window(self.current_img.convert('L').convert('RGB'), "Grayscale")
    def filter_sepia(self):
        cv_img = self.pil_to_cv2(self.current_img).astype(np.float32)
        sepia_kernel = np.array([[0.272, 0.534, 0.131], [0.349, 0.686, 0.168], [0.393, 0.769, 0.189]])
        sepia = cv2.transform(cv_img, sepia_kernel)
        self.show_effect_in_window(self.cv2_to_pil(np.clip(sepia, 0, 255).astype(np.uint8)), "Sepia")
    
    def filter_rgb_shift(self):
        cv_img = self.pil_to_cv2(self.current_img)
        b, g, r = cv2.split(cv_img)
        self.show_effect_in_window(self.cv2_to_pil(cv2.merge([cv2.GaussianBlur(b, (7,7), 0), g, r])), "RGB Shift")

    def filter_posterize(self): self.show_effect_in_window(ImageOps.posterize(self.current_img, 4), "Posterize")
    def filter_solarize(self): self.show_effect_in_window(ImageOps.solarize(self.current_img, 128), "Solarize")
    
    def adj_brightness(self): self.show_effect_in_window(ImageEnhance.Brightness(self.current_img).enhance(1.4), "Brightness")
    def adj_contrast(self): self.show_effect_in_window(ImageEnhance.Contrast(self.current_img).enhance(1.5), "Contrast")
    def adj_saturation(self): self.show_effect_in_window(ImageEnhance.Color(self.current_img).enhance(1.6), "Saturation")
    def adj_hue(self):
        hsv = cv2.cvtColor(self.pil_to_cv2(self.current_img), cv2.COLOR_BGR2HSV)
        hsv[:,:,0] = (hsv[:,:,0] + 30) % 180
        self.show_effect_in_window(self.cv2_to_pil(cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)), "Hue Shift")

    def effect_gaussian_blur(self): self.show_effect_in_window(self.current_img.filter(ImageFilter.GaussianBlur(5)), "Blur")
    def effect_pixelize(self):
        w, h = self.current_img.size
        self.show_effect_in_window(self.current_img.resize((50,50)).resize((w,h), Image.NEAREST), "Pixelize")
    def effect_oil_paint(self): self.show_effect_in_window(self.current_img.filter(ImageFilter.EDGE_ENHANCE_MORE), "Edge Enhance")

    def edge_canny(self):
        gray = cv2.cvtColor(self.pil_to_cv2(self.current_img), cv2.COLOR_BGR2GRAY)
        self.show_effect_in_window(self.cv2_to_pil(cv2.cvtColor(cv2.Canny(gray, 100, 200), cv2.COLOR_GRAY2BGR)), "Canny")
    
    def edge_sobel(self):
        gray = cv2.cvtColor(self.pil_to_cv2(self.current_img), cv2.COLOR_BGR2GRAY)
        sobel = np.hypot(cv2.Sobel(gray, cv2.CV_64F, 1, 0), cv2.Sobel(gray, cv2.CV_64F, 0, 1))
        self.show_effect_in_window(self.cv2_to_pil(cv2.cvtColor(np.uint8(np.clip(sobel, 0, 255)), cv2.COLOR_GRAY2BGR)), "Sobel")

    def edge_laplacian(self):
        gray = cv2.cvtColor(self.pil_to_cv2(self.current_img), cv2.COLOR_BGR2GRAY)
        lap = cv2.Laplacian(gray, cv2.CV_64F)
        self.show_effect_in_window(self.cv2_to_pil(cv2.cvtColor(np.uint8(np.absolute(lap)), cv2.COLOR_GRAY2BGR)), "Laplacian")

    def edge_contours(self):
        img = self.pil_to_cv2(self.current_img)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cnts, _ = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(img, cnts, -1, (0, 255, 0), 2)
        self.show_effect_in_window(self.cv2_to_pil(img), "Contours")

    def transform_rotate90(self): self.show_effect_in_window(self.current_img.rotate(90, expand=True), "Rotate 90")
    def transform_flip_h(self): self.show_effect_in_window(self.current_img.transpose(Image.FLIP_LEFT_RIGHT), "Flip H")
    def transform_flip_v(self): self.show_effect_in_window(self.current_img.transpose(Image.FLIP_TOP_BOTTOM), "Flip V")
    def transform_mirror(self):
        w, h = self.current_img.size
        left = self.current_img.crop((0,0,w//2,h))
        res = self.current_img.copy()
        res.paste(left.transpose(Image.FLIP_LEFT_RIGHT), (w//2, 0))
        self.show_effect_in_window(res, "Mirror")

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedImageEditor(root)
    root.mainloop()
