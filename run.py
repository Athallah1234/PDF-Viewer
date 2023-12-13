import fitz
import tkinter as tk
from tkinter import ttk, filedialog

class PDFViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Viewer")
        self.root.geometry("800x600")

        # Variables
        self.current_page = tk.IntVar()
        self.total_pages = tk.IntVar()
        self.zoom_factor = tk.DoubleVar(value=1.0)
        self.highlight_mode = tk.BooleanVar(value=False)
        self.fit_width = tk.BooleanVar(value=False)
        self.fit_height = tk.BooleanVar(value=False)

        # Create Widgets
        self.create_widgets()

    def create_widgets(self):
        # Menu Bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)

        # Toolbar
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(toolbar, text="Previous", command=self.previous_page).pack(side=tk.LEFT)
        ttk.Label(toolbar, text="Page:").pack(side=tk.LEFT)
        ttk.Entry(toolbar, textvariable=self.current_page, width=5).pack(side=tk.LEFT)
        ttk.Label(toolbar, text="/").pack(side=tk.LEFT)
        ttk.Label(toolbar, textvariable=self.total_pages).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Next", command=self.next_page).pack(side=tk.LEFT)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Zoom In", command=self.zoom_in).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Zoom Out", command=self.zoom_out).pack(side=tk.LEFT)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Rotate Clockwise", command=self.rotate_clockwise).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Rotate Counterclockwise", command=self.rotate_counterclockwise).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Fit Width", command=self.fit_width_mode).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Fit Height", command=self.fit_height_mode).pack(side=tk.LEFT)

        # PDF Canvas
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.scroll_canvas)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Status Bar
        self.statusbar = ttk.Label(self.root, text="Ready", anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])

        if file_path:
            self.load_pdf(file_path)

    def load_pdf(self, file_path):
        self.doc = fitz.open(file_path)
        self.total_pages.set(self.doc.page_count)
        self.current_page.set(1)

        self.show_page()
        self.update_statusbar()

    def show_page(self):
        page_number = self.current_page.get() - 1
        page = self.doc.load_page(page_number)
        zoom = self.zoom_factor.get()

        if self.fit_width.get():
            zoom = self.calculate_fit_width_zoom(page)
        elif self.fit_height.get():
            zoom = self.calculate_fit_height_zoom(page)

        img = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        photo = tk.PhotoImage(data=img.tobytes("ppm"))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.image = photo
        self.update_statusbar()

    def previous_page(self):
        current_page = self.current_page.get()
        if current_page > 1:
            self.current_page.set(current_page - 1)
            self.show_page()
            self.update_statusbar()

    def next_page(self):
        current_page = self.current_page.get()
        if current_page < self.total_pages.get():
            self.current_page.set(current_page + 1)
            self.show_page()
            self.update_statusbar()

    def scroll_canvas(self, *args):
        self.canvas.yview(*args)

    def zoom_in(self):
        current_zoom = float(self.zoom_factor.get())
        if current_zoom < 2.0:
            new_zoom = round(current_zoom + 0.1, 1)
            self.zoom_factor.set(new_zoom)
            self.show_page()
            self.update_statusbar()

    def zoom_out(self):
        current_zoom = float(self.zoom_factor.get())
        if current_zoom > 0.2:
            new_zoom = round(current_zoom - 0.1, 1)
            self.zoom_factor.set(new_zoom)
            self.show_page()
            self.update_statusbar()

    def validate_page_entry(self, value):
        return value.isdigit() and 1 <= int(value) <= self.total_pages.get()

    def rotate_clockwise(self):
        self.rotate_page(90)

    def rotate_counterclockwise(self):
        self.rotate_page(-90)

    def rotate_page(self, angle):
        page_number = self.current_page.get() - 1
        page = self.doc[page_number]
        page.set_rotation(page.rotation + angle)
        self.show_page()
        self.update_statusbar()

    def update_statusbar(self):
        page_number = self.current_page.get()
        total_pages = self.total_pages.get()
        zoom = int(self.zoom_factor.get() * 100)

        status_text = f"Page {page_number} of {total_pages} | Zoom: {zoom}%"
        self.statusbar.config(text=status_text)

    def fit_width_mode(self):
        self.fit_width.set(not self.fit_width.get())
        self.fit_height.set(False)  # Ensure only one mode is active
        self.show_page()

    def fit_height_mode(self):
        self.fit_height.set(not self.fit_height.get())
        self.fit_width.set(False)  # Ensure only one mode is active
        self.show_page()

    def calculate_fit_width_zoom(self, page):
        canvas_width = self.canvas.winfo_width()
        page_width = page.rect.width
        return canvas_width / page_width
    
    def calculate_fit_height_zoom(self, page):
        canvas_height = self.canvas.winfo_height()
        page_height = page.rect.height
        return canvas_height / page_height

if __name__ == "__main__":
    root = tk.Tk()
    pdf_viewer = PDFViewer(root)
    root.mainloop()

