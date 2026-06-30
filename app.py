import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

from ComicMerge import ComicMerge


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("ComicMerge")
        self.geometry("760x620")

        self.grid_columnconfigure(1, weight=1)

        # =====================
        # Comic Folder
        # =====================

        ctk.CTkLabel(self, text="Comic Folder").grid(
            row=0, column=0, padx=15, pady=(20, 10), sticky="w"
        )

        self.comic_folder = ctk.StringVar()

        ctk.CTkEntry(
            self,
            textvariable=self.comic_folder,
            width=450
        ).grid(row=0, column=1, padx=5)

        ctk.CTkButton(
            self,
            text="Browse",
            width=90,
            command=self.pick_comic_folder
        ).grid(row=0, column=2, padx=15)

        # =====================
        # Output Folder
        # =====================

        ctk.CTkLabel(self, text="Output Folder").grid(
            row=1,
            column=0,
            padx=15,
            pady=10,
            sticky="w"
        )

        self.output_folder = ctk.StringVar()

        ctk.CTkEntry(
            self,
            textvariable=self.output_folder,
            width=450
        ).grid(row=1, column=1)

        ctk.CTkButton(
            self,
            text="Browse",
            width=90,
            command=self.pick_output_folder
        ).grid(row=1, column=2, padx=15)

        # =====================
        # Output File
        # =====================

        ctk.CTkLabel(self, text="Output Filename").grid(
            row=2,
            column=0,
            padx=15,
            pady=10,
            sticky="w"
        )

        self.output_name = ctk.StringVar(value="merged.cbz")

        ctk.CTkEntry(
            self,
            textvariable=self.output_name,
            width=450
        ).grid(row=2, column=1, columnspan=2, sticky="ew", padx=(0,15))

        # =====================
        # Prefix
        # =====================

        ctk.CTkLabel(self, text="Prefix").grid(
            row=3,
            column=0,
            padx=15,
            pady=10,
            sticky="w"
        )

        self.prefix = ctk.StringVar()

        ctk.CTkEntry(
            self,
            textvariable=self.prefix,
            width=250
        ).grid(row=3, column=1, sticky="w")

        # =====================
        # Range
        # =====================

        ctk.CTkLabel(self, text="Start").grid(
            row=4,
            column=0,
            padx=15,
            pady=10,
            sticky="w"
        )

        self.start = ctk.StringVar()

        ctk.CTkEntry(
            self,
            textvariable=self.start,
            width=100
        ).grid(row=4, column=1, sticky="w")

        ctk.CTkLabel(self, text="End").grid(
            row=5,
            column=0,
            padx=15,
            pady=10,
            sticky="w"
        )

        self.end = ctk.StringVar()

        ctk.CTkEntry(
            self,
            textvariable=self.end,
            width=100
        ).grid(row=5, column=1, sticky="w")

        # =====================

        self.verbose = ctk.BooleanVar()

        ctk.CTkCheckBox(
            self,
            text="Verbose",
            variable=self.verbose
        ).grid(row=6, column=1, sticky="w", pady=10)

        # =====================

        self.progress = ctk.CTkProgressBar(self, width=650)
        self.progress.grid(row=7, column=0, columnspan=3, padx=20, pady=10)
        self.progress.set(0)

        # =====================

        self.merge_btn = ctk.CTkButton(
            self,
            text="Merge Comics",
            height=42,
            command=self.start_merge
        )

        self.merge_btn.grid(
            row=8,
            column=0,
            columnspan=3,
            padx=20,
            pady=10,
            sticky="ew"
        )

        # =====================

        self.log = ctk.CTkTextbox(
            self,
            width=700,
            height=220
        )

        self.log.grid(
            row=9,
            column=0,
            columnspan=3,
            padx=20,
            pady=(10,20),
            sticky="nsew"
        )

    def write(self, text):
        self.log.insert("end", text + "\n")
        self.log.see("end")

    def pick_comic_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.comic_folder.set(folder)

    def pick_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder.set(folder)

    def start_merge(self):
        threading.Thread(target=self.merge, daemon=True).start()

    def merge(self):

        self.merge_btn.configure(state="disabled")

        try:

            self.progress.set(0)

            comic_folder = self.comic_folder.get()
            output_folder = self.output_folder.get()
            output = self.output_name.get()

            if not comic_folder:
                raise Exception("Comic folder belum dipilih.")

            if not output_folder:
                raise Exception("Output folder belum dipilih.")

            if not output.endswith(".cbz"):
                output += ".cbz"

            os.chdir(comic_folder)

            if self.prefix.get():

                comics = ComicMerge.comics_from_prefix(
                    self.prefix.get()
                )

            elif self.start.get() and self.end.get():

                comics = ComicMerge.comics_from_indices(
                    int(self.start.get()),
                    int(self.end.get())
                )

            else:

                comics = ComicMerge.comics_from_indices(0, -1)

            comics.sort()

            self.write(f"{len(comics)} comics ditemukan.")

            self.progress.set(0.3)

            merger = ComicMerge(
                os.path.join(output_folder, output),
                comics,
                self.verbose.get()
            )

            self.write("Merging...")

            merger.merge()

            self.progress.set(1)

            self.write("Selesai.")

            messagebox.showinfo(
                "Success",
                "Merge berhasil!"
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )

            self.write(str(e))

        finally:

            self.merge_btn.configure(state="normal")


App().mainloop()