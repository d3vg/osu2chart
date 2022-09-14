"""
osu2chart.pyw

A GUI tool for converting osu!mania maps to Clone Hero charts.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.ttk as ttk

from os.path import exists

from osu import Osu, OsuFile
from chart import Chart

# Template code generated in Pygubu Designer
class Osu2ChartApp:
    def __init__(self, master=None):
        # Root window
        self.top_main_frame = tk.Tk() if master is None else tk.Toplevel(master)
        self.top_main_frame.configure(height=320, padx=8, pady=8, width=480)
        # self.top_main_frame.geometry("480x362")
        # self.top_main_frame.minsize(328, 362)
        self.top_main_frame.geometry("480x330")
        self.top_main_frame.minsize(328, 330)
        self.top_main_frame.resizable(True, False)
        self.top_main_frame.title("osu2chart")

        # Control variables
        self._easy_path = tk.StringVar()
        self._medium_path = tk.StringVar()
        self._hard_path = tk.StringVar()
        self._expert_path = tk.StringVar()

        # self._include_bg = tk.IntVar(value=1)
        self._use_unicode_metadata = tk.IntVar(value=0)
        self._use_tags_as_genre = tk.IntVar(value=0)

        self._preview_length = tk.DoubleVar(value=0.0)
        self._resolution = tk.IntVar(value=192)

        self._save_path = tk.StringVar()

        # UI
        self.lbf_difficulties = ttk.Labelframe(self.top_main_frame)
        self.lbf_difficulties.configure(
            height=200, padding="4 4 4 4", text=".osu files"
        )

        self.lbl_easy = ttk.Label(self.lbf_difficulties)
        self.lbl_easy.configure(text="Easy")
        self.lbl_easy.grid(column=0, padx=4, row=0, sticky="e")

        self.ent_easy = ttk.Entry(self.lbf_difficulties, textvariable=self._easy_path)
        self.ent_easy.configure(width=9999)
        self.ent_easy.grid(column=1, columnspan=1, row=0)

        self.btn_easy = ttk.Button(self.lbf_difficulties, command=lambda: self.ask_for_osu_file(self._easy_path))
        self.btn_easy.configure(text="...", width=3)
        self.btn_easy.grid(column=2, row=0, sticky="w")

        self.lbl_medium = ttk.Label(self.lbf_difficulties)
        self.lbl_medium.configure(text="Medium")
        self.lbl_medium.grid(column=0, padx=4, row=1, sticky="e")

        self.lbl_hard = ttk.Label(self.lbf_difficulties)
        self.lbl_hard.configure(text="Hard")
        self.lbl_hard.grid(column=0, padx=4, row=2, sticky="e")

        self.lbl_expert = ttk.Label(self.lbf_difficulties)
        self.lbl_expert.configure(text="Expert")
        self.lbl_expert.grid(column=0, padx=4, row=3, sticky="e")

        self.ent_medium = ttk.Entry(self.lbf_difficulties, textvariable=self._medium_path)
        self.ent_medium.configure(width=9999)
        self.ent_medium.grid(column=1, row=1)

        self.ent_hard = ttk.Entry(self.lbf_difficulties, textvariable=self._hard_path)
        self.ent_hard.configure(width=9999)
        self.ent_hard.grid(column=1, row=2)

        self.ent_expert = ttk.Entry(self.lbf_difficulties, textvariable=self._expert_path)
        self.ent_expert.configure(width=9999)
        self.ent_expert.grid(column=1, row=3)

        self.btn_medium = ttk.Button(self.lbf_difficulties, command=lambda: self.ask_for_osu_file(self._medium_path))
        self.btn_medium.configure(text="...", width=3)
        self.btn_medium.grid(column=2, row=1, sticky="w")

        self.btn_hard = ttk.Button(self.lbf_difficulties, command=lambda: self.ask_for_osu_file(self._hard_path))
        self.btn_hard.configure(text="...", width=3)
        self.btn_hard.grid(column=2, row=2, sticky="w")

        self.btn_expert = ttk.Button(self.lbf_difficulties, command=lambda: self.ask_for_osu_file(self._expert_path))
        self.btn_expert.configure(text="...", width=3)
        self.btn_expert.grid(column=2, row=3, sticky="w")

        self.lbf_difficulties.pack(fill="x", side="top")
        self.lbf_difficulties.grid_anchor("center")
        self.lbf_difficulties.columnconfigure(0, minsize=56, weight=1)
        self.lbf_difficulties.columnconfigure(1, minsize=200, weight=8)
        self.lbf_difficulties.columnconfigure(2, minsize=29, weight=1)

        self.lbf_options = ttk.Labelframe(self.top_main_frame)
        self.lbf_options.configure(height=200, padding="4 4 4 4", text="Options")

        self.chk_unicode = ttk.Checkbutton(self.lbf_options, variable=self._use_unicode_metadata)
        self.chk_unicode.configure(text="Use unicode metadata")
        self.chk_unicode.grid(column=0, columnspan=2, row=0, sticky="n")

        self.lbl_preview_length = ttk.Label(self.lbf_options)
        self.lbl_preview_length.configure(
            padding="0 0 4 0", text="Preview length (in seconds)"
        )
        self.lbl_preview_length.grid(column=0, row=3, sticky="e")

        self.lbl_resolution = ttk.Label(self.lbf_options)
        self.lbl_resolution.configure(padding="0 0 4 0", text="Resolution")
        self.lbl_resolution.grid(column=0, row=4, sticky="e")

        self.spb_preview_length = ttk.Spinbox(self.lbf_options, textvariable=self._preview_length)
        self.spb_preview_length.configure(from_=0, increment=0.5, to=999, wrap="false")
        self.spb_preview_length.set(0)
        self.spb_preview_length.grid(column=1, row=3)

        self.spb_resolution = ttk.Spinbox(self.lbf_options, textvariable=self._resolution)
        self.spb_resolution.configure(from_=192, increment=1, to=480, wrap="false")
        self.spb_resolution.set(192)
        self.spb_resolution.grid(column=1, row=4)

        self.chk_tags_as_genre = ttk.Checkbutton(self.lbf_options, variable=self._use_tags_as_genre)
        self.chk_tags_as_genre.configure(text="Use tags as genre")
        self.chk_tags_as_genre.grid(column=0, columnspan=2, row=1, sticky="n")

        """
        # TODO: Optionally include BG / video in song package
        # NOTE: Need to do more research on how Clone Hero handles custom backgrounds,
        #       so putting this on hold for now.
        self.chk_include_bg = ttk.Checkbutton(self.lbf_options, variable=self._include_bg)
        self.chk_include_bg.configure(text="Include background / video")
        self.chk_include_bg.grid(column=0, columnspan=2, row=2, sticky="n")
        """

        self.lbf_options.pack(fill="x", side="top")
        self.lbf_options.grid_anchor("center")
        self.lbf_options.rowconfigure("all", pad=4)

        self.frm_convert = ttk.Frame(self.top_main_frame)
        self.frm_convert.configure(height=200, padding="4 12 4 4", width=200)

        self.lbl_save_directory = ttk.Label(self.frm_convert)
        self.lbl_save_directory.configure(text="Save directory")
        self.lbl_save_directory.grid(column=0, padx=4, row=0, sticky="e")

        self.ent_save_directory = ttk.Entry(self.frm_convert, textvariable=self._save_path)
        self.ent_save_directory.configure(width=9999)
        self.ent_save_directory.grid(column=1, row=0, pady=4)

        self.btn_save_directory = ttk.Button(self.frm_convert, command=lambda: self.ask_for_save_directory(self._save_path))
        self.btn_save_directory.configure(text="...", width=3)
        self.btn_save_directory.grid(column=2, row=0)

        self.btn_convert = ttk.Button(self.frm_convert, command=self.convert)
        self.btn_convert.configure(text="Convert")
        self.btn_convert.grid(column=0, columnspan=3, row=1)

        self.frm_convert.pack(fill="x", side="top")
        self.frm_convert.grid_anchor("center")
        self.frm_convert.columnconfigure(0, minsize=86, weight=1)
        self.frm_convert.columnconfigure(1, minsize=200, weight=8)
        self.frm_convert.columnconfigure(2, minsize=29, weight=1)

        # Main widget
        self.mainwindow = self.top_main_frame

    def ask_for_osu_file(self, entry_variable):
        osu_fname = filedialog.askopenfilename(title="Please select a .osu file", filetypes=[("osu! file", "*.osu")])

        if osu_fname != "":
            entry_variable.set(osu_fname)

    def ask_for_save_directory(self, entry_variable):
        save_directory = filedialog.askdirectory(title="Please select a directory for the resulting audio/chart file")

        if save_directory != "":
            entry_variable.set(save_directory)

    def convert(self):
        if self._save_path.get() == "":
            messagebox.showerror(title="osu2chart", message="Please set the save directory.")
            return

        osu_file = {
            "easy": Osu.create_from_path(self._easy_path.get()),
            "medium": Osu.create_from_path(self._medium_path.get()),
            "hard": Osu.create_from_path(self._hard_path.get()),
            "expert": Osu.create_from_path(self._expert_path.get())
        }

        chart = None

        # Only try to generate the chart if at least one OsuFile exists
        for f in osu_file:
            if type(osu_file[f]) is OsuFile:
                if self._resolution.get() <= 0:
                    messagebox.showerror(title="osu2chart", message="Resolution must be greater than 0.")
                    return

                if self._preview_length.get() < 0:
                    messagebox.showerror(title="osu2chart", message="Preview length cannot be a negative number.")
                    return

                chart = Chart.create_from_osu(osu_file[f],
                    resolution=self._resolution.get(),
                    preview_length=self._preview_length.get(),
                    use_unicode_metadata=self._use_unicode_metadata.get(),
                    use_tags_as_genre=self._use_tags_as_genre.get(),
                    expert=osu_file["expert"],
                    hard=osu_file["hard"],
                    medium=osu_file["medium"],
                    easy=osu_file["easy"])
                break
        
        if chart is not None:
            chart_fname = self._save_path.get() + "/notes.chart"
            if exists(chart_fname):
                if not messagebox.askyesno(title="osu2chart", message="A chart already exists in this directory.\nProceed with the conversion and overwrite the file?"):
                    messagebox.showwarning(title="osu2chart", message="Conversion aborted.")
                    return

            chart.export(chart_fname)
            messagebox.showinfo(title="osu2chart", message="Conversion complete!")
        else:
            messagebox.showerror(title="osu2chart", message="Failed to convert!\nPlease check the path(s) to your .osu file(s).")

    def run(self):
        self.mainwindow.mainloop()

if __name__ == "__main__":
    app = Osu2ChartApp()
    app.run()