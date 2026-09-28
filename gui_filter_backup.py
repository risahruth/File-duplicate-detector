import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os


class DuplicateDetectorGUI:

    def __init__(self, root):
        self.root = root

        self.root.title("Duplicate File Detector")
        self.root.geometry("1100x750")
        self.root.minsize(900, 650)

        self.root.configure(bg="#f4f1f8")

        self.directory = ""

        # Stores all duplicate rows
        self.all_results = []

        self.create_styles()
        self.create_header()
        self.create_scan_section()
        self.create_statistics()
        self.create_filter_section()
        self.create_results_section()
        self.create_footer()

    # ---------------------------------------------------------
    # STYLES
    # ---------------------------------------------------------

    def create_styles(self):
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Treeview",
            background="#ffffff",
            foreground="#333333",
            rowheight=32,
            fieldbackground="#ffffff",
            font=("Arial", 10)
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 10, "bold")
        )

    # ---------------------------------------------------------
    # HEADER
    # ---------------------------------------------------------

    def create_header(self):
        header = tk.Frame(
            self.root,
            bg="#6c5b7b",
            height=90
        )

        header.pack(fill="x")
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="Duplicate File Detector",
            bg="#6c5b7b",
            fg="white",
            font=("Arial", 24, "bold")
        )

        title.pack(
            side="left",
            padx=30,
            pady=20
        )

        subtitle = tk.Label(
            header,
            text="Linux File System Analysis",
            bg="#6c5b7b",
            fg="#eee8f4",
            font=("Arial", 10)
        )

        subtitle.pack(
            side="right",
            padx=30
        )

    # ---------------------------------------------------------
    # SCAN SECTION
    # ---------------------------------------------------------

    def create_scan_section(self):

        frame = tk.Frame(
            self.root,
            bg="#f4f1f8"
        )

        frame.pack(
            fill="x",
            padx=30,
            pady=20
        )

        label = tk.Label(
            frame,
            text="Scan Location",
            bg="#f4f1f8",
            fg="#333333",
            font=("Arial", 11, "bold")
        )

        label.pack(
            anchor="w",
            pady=(0, 6)
        )

        path_frame = tk.Frame(
            frame,
            bg="#f4f1f8"
        )

        path_frame.pack(fill="x")

        self.path_entry = tk.Entry(
            path_frame,
            font=("Arial", 11),
            relief="solid",
            bd=1
        )

        self.path_entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=8
        )

        browse_button = tk.Button(
            path_frame,
            text="Browse",
            command=self.browse_directory,
            bg="#d9c8e8",
            fg="#333333",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2"
        )

        browse_button.pack(
            side="left",
            padx=(10, 0)
        )

        self.scan_button = tk.Button(
            frame,
            text="SCAN NOW",
            command=self.scan,
            bg="#6c5b7b",
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            padx=30,
            pady=10,
            cursor="hand2"
        )

        self.scan_button.pack(pady=15)

        self.status_label = tk.Label(
            frame,
            text="Ready to scan",
            bg="#f4f1f8",
            fg="#777777",
            font=("Arial", 9)
        )

        self.status_label.pack()

    # ---------------------------------------------------------
    # STATISTICS
    # ---------------------------------------------------------

    def create_statistics(self):

        frame = tk.Frame(
            self.root,
            bg="#f4f1f8"
        )

        frame.pack(
            fill="x",
            padx=30,
            pady=5
        )

        self.files_value = self.create_stat_card(
            frame,
            "Files Scanned",
            "0"
        )

        self.groups_value = self.create_stat_card(
            frame,
            "Duplicate Groups",
            "0"
        )

        self.duplicates_value = self.create_stat_card(
            frame,
            "Duplicate Files",
            "0"
        )

        self.savings_value = self.create_stat_card(
            frame,
            "Recoverable Space",
            "0 B"
        )

    def create_stat_card(
        self,
        parent,
        title,
        value
    ):

        card = tk.Frame(
            parent,
            bg="white",
            bd=1,
            relief="solid"
        )

        card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        title_label = tk.Label(
            card,
            text=title,
            bg="white",
            fg="#777777",
            font=("Arial", 9)
        )

        title_label.pack(
            pady=(12, 2)
        )

        value_label = tk.Label(
            card,
            text=value,
            bg="white",
            fg="#6c5b7b",
            font=("Arial", 20, "bold")
        )

        value_label.pack(
            pady=(0, 12)
        )

        return value_label

    # ---------------------------------------------------------
    # FILTER SECTION
    # ---------------------------------------------------------

    def create_filter_section(self):

        frame = tk.Frame(
            self.root,
            bg="#f4f1f8"
        )

        frame.pack(
            fill="x",
            padx=30,
            pady=(15, 5)
        )

        search_label = tk.Label(
            frame,
            text="Search Duplicate Files",
            bg="#f4f1f8",
            fg="#333333",
            font=("Arial", 10, "bold")
        )

        search_label.pack(
            side="left",
            padx=(0, 10)
        )

        self.search_entry = tk.Entry(
            frame,
            font=("Arial", 10),
            relief="solid",
            bd=1
        )

        self.search_entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=6
        )

        self.search_entry.bind(
            "<KeyRelease>",
            self.filter_results
        )

        self.type_filter = ttk.Combobox(
            frame,
            state="readonly",
            values=[
                "All Files",
                "Images",
                "Documents",
                "Videos",
                "Audio",
                "Archives",
                "Other"
            ],
            width=15
        )

        self.type_filter.set("All Files")

        self.type_filter.pack(
            side="left",
            padx=(10, 0),
            ipady=4
        )

        self.type_filter.bind(
            "<<ComboboxSelected>>",
            self.filter_results
        )

        clear_button = tk.Button(
            frame,
            text="Clear",
            command=self.clear_filter,
            bg="#d9c8e8",
            fg="#333333",
            font=("Arial", 9, "bold"),
            relief="flat",
            padx=15,
            pady=6,
            cursor="hand2"
        )

        clear_button.pack(
            side="left",
            padx=(10, 0)
        )

    # ---------------------------------------------------------
    # RESULTS SECTION
    # ---------------------------------------------------------

    def create_results_section(self):

        frame = tk.Frame(
            self.root,
            bg="#f4f1f8"
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=15
        )

        label = tk.Label(
            frame,
            text="Duplicate Files",
            bg="#f4f1f8",
            fg="#333333",
            font=("Arial", 13, "bold")
        )

        label.pack(
            anchor="w",
            pady=(0, 8)
        )

        tree_frame = tk.Frame(
            frame,
            bg="white"
        )

        tree_frame.pack(
            fill="both",
            expand=True
        )

        columns = (
            "group",
            "file",
            "type",
            "size"
        )

        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings"
        )

        self.tree.heading(
            "group",
            text="Group"
        )

        self.tree.heading(
            "file",
            text="File Path"
        )

        self.tree.heading(
            "type",
            text="Type"
        )

        self.tree.heading(
            "size",
            text="Size"
        )

        self.tree.column(
            "group",
            width=70,
            anchor="center"
        )

        self.tree.column(
            "file",
            width=620
        )

        self.tree.column(
            "type",
            width=120,
            anchor="center"
        )

        self.tree.column(
            "size",
            width=120,
            anchor="center"
        )

        scrollbar = ttk.Scrollbar(
            tree_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

    # ---------------------------------------------------------
    # FOOTER
    # ---------------------------------------------------------

    def create_footer(self):

        frame = tk.Frame(
            self.root,
            bg="#f4f1f8"
        )

        frame.pack(
            fill="x",
            padx=30,
            pady=(0, 20)
        )

        self.type_summary = tk.Label(
            frame,
            text="Duplicate types: No scan performed",
            bg="#f4f1f8",
            fg="#666666",
            font=("Arial", 9)
        )

        self.type_summary.pack(
            side="left"
        )

        export_button = tk.Button(
            frame,
            text="Export Report",
            command=self.export_report,
            bg="#d9c8e8",
            fg="#333333",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2"
        )

        export_button.pack(
            side="right"
        )

    # ---------------------------------------------------------
    # BROWSE
    # ---------------------------------------------------------

    def browse_directory(self):

        directory = filedialog.askdirectory(
            title="Select directory to scan"
        )

        if directory:

            self.directory = directory

            self.path_entry.delete(
                0,
                tk.END
            )

            self.path_entry.insert(
                0,
                directory
            )

    # ---------------------------------------------------------
    # SCAN
    # ---------------------------------------------------------

    def scan(self):

        directory = self.path_entry.get().strip()

        if not directory:

            messagebox.showwarning(
                "No Directory",
                "Please select a directory first."
            )

            return

        if not os.path.isdir(directory):

            messagebox.showerror(
                "Invalid Directory",
                "The selected path is not a valid directory."
            )

            return

        self.scan_button.config(
            state="disabled"
        )

        self.status_label.config(
            text="Scanning..."
        )

        self.root.update_idletasks()

        try:

            result = subprocess.run(
                [
                    "./duplicate_detector",
                    directory
                ],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(
                    os.path.abspath(__file__)
                )
            )

            if result.returncode != 0:

                messagebox.showerror(
                    "Scan Error",
                    result.stderr
                )

                return

            self.read_results()

            self.status_label.config(
                text="Scan completed successfully"
            )

        except Exception as error:

            messagebox.showerror(
                "Error",
                str(error)
            )

        finally:

            self.scan_button.config(
                state="normal"
            )

    # ---------------------------------------------------------
    # READ RESULTS
    # ---------------------------------------------------------

    def read_results(self):

        result_file = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "results.txt"
        )

        if not os.path.exists(result_file):

            messagebox.showerror(
                "Error",
                "results.txt was not created."
            )

            return

        with open(
            result_file,
            "r"
        ) as file:

            lines = file.readlines()

        files_scanned = 0
        groups = 0
        duplicate_files = 0
        savings = 0

        current_group = 0
        current_size = "0 B"

        self.all_results = []

        self.tree.delete(
            *self.tree.get_children()
        )

        for line in lines:

            line = line.strip()

            if line.startswith(
                "FILES_SCANNED="
            ):

                files_scanned = int(
                    line.split("=")[1]
                )

            elif line.startswith(
                "DUPLICATE_GROUPS="
            ):

                groups = int(
                    line.split("=")[1]
                )

            elif line.startswith(
                "DUPLICATE_FILES="
            ):

                duplicate_files = int(
                    line.split("=")[1]
                )

            elif line.startswith(
                "POTENTIAL_SAVINGS="
            ):

                savings = int(
                    line.split("=")[1]
                )

            elif line == "GROUP":

                current_group += 1

            elif line.startswith(
                "SIZE_HUMAN="
            ):

                current_size = line.split(
                    "=",
                    1
                )[1]

            elif line.startswith(
                "FILE="
            ):

                path = line.split(
                    "=",
                    1
                )[1]

                file_type = self.get_file_type(
                    path
                )

                result_data = {
                    "group": current_group,
                    "file": path,
                    "type": file_type,
                    "size": current_size
                }

                self.all_results.append(
                    result_data
                )

        self.files_value.config(
            text=str(files_scanned)
        )

        self.groups_value.config(
            text=str(groups)
        )

        self.duplicates_value.config(
            text=str(duplicate_files)
        )

        self.savings_value.config(
            text=self.format_size(savings)
        )

        self.display_results(
            self.all_results
        )

        self.update_type_summary()

    # ---------------------------------------------------------
    # FILE TYPE DETECTION
    # ---------------------------------------------------------

    def get_file_type(self, path):

        extension = os.path.splitext(
            path
        )[1].lower()

        image_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".webp",
            ".svg",
            ".tiff"
        }

        document_extensions = {
            ".txt",
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".csv",
            ".odt"
        }

        video_extensions = {
            ".mp4",
            ".mkv",
            ".avi",
            ".mov",
            ".wmv",
            ".flv",
            ".webm"
        }

        audio_extensions = {
            ".mp3",
            ".wav",
            ".aac",
            ".flac",
            ".ogg",
            ".m4a"
        }

        archive_extensions = {
            ".zip",
            ".tar",
            ".gz",
            ".bz2",
            ".7z",
            ".rar"
        }

        if extension in image_extensions:
            return "Image"

        if extension in document_extensions:
            return "Document"

        if extension in video_extensions:
            return "Video"

        if extension in audio_extensions:
            return "Audio"

        if extension in archive_extensions:
            return "Archive"

        if extension == "":
            return "No Extension"

        return "Other"

    # ---------------------------------------------------------
    # DISPLAY RESULTS
    # ---------------------------------------------------------

    def display_results(self, results):

        self.tree.delete(
            *self.tree.get_children()
        )

        for item in results:

            self.tree.insert(
                "",
                "end",
                values=(
                    item["group"],
                    item["file"],
                    item["type"],
                    item["size"]
                )
            )

    # ---------------------------------------------------------
    # FILTER RESULTS
    # ---------------------------------------------------------

    def filter_results(self, event=None):

        search_text = self.search_entry.get().lower().strip()

        selected_type = self.type_filter.get()

        filtered = []

        for item in self.all_results:

            path_match = (
                search_text == ""
                or search_text in item["file"].lower()
            )

            type_match = True

            if selected_type == "Images":
                type_match = item["type"] == "Image"

            elif selected_type == "Documents":
                type_match = item["type"] == "Document"

            elif selected_type == "Videos":
                type_match = item["type"] == "Video"

            elif selected_type == "Audio":
                type_match = item["type"] == "Audio"

            elif selected_type == "Archives":
                type_match = item["type"] == "Archive"

            elif selected_type == "Other":
                type_match = item["type"] in {
                    "Other",
                    "No Extension"
                }

            if path_match and type_match:
                filtered.append(item)

        self.display_results(
            filtered
        )

    # ---------------------------------------------------------
    # CLEAR FILTER
    # ---------------------------------------------------------

    def clear_filter(self):

        self.search_entry.delete(
            0,
            tk.END
        )

        self.type_filter.set(
            "All Files"
        )

        self.display_results(
            self.all_results
        )

    # ---------------------------------------------------------
    # TYPE SUMMARY
    # ---------------------------------------------------------

    def update_type_summary(self):

        if not self.all_results:

            self.type_summary.config(
                text="Duplicate types: None"
            )

            return

        counts = {}

        for item in self.all_results:

            file_type = item["type"]

            counts[file_type] = (
                counts.get(file_type, 0) + 1
            )

        parts = []

        for file_type, count in sorted(
            counts.items()
        ):

            parts.append(
                f"{file_type}: {count}"
            )

        self.type_summary.config(
            text="Duplicate types: "
            + "  |  ".join(parts)
        )

    # ---------------------------------------------------------
    # FORMAT SIZE
    # ---------------------------------------------------------

    def format_size(self, size):

        if size >= 1024 * 1024 * 1024:

            return f"{size / (1024 * 1024 * 1024):.2f} GB"

        elif size >= 1024 * 1024:

            return f"{size / (1024 * 1024):.2f} MB"

        elif size >= 1024:

            return f"{size / 1024:.2f} KB"

        else:

            return f"{size} B"

    # ---------------------------------------------------------
    # EXPORT REPORT
    # ---------------------------------------------------------

    def export_report(self):

        result_file = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "results.txt"
        )

        if not os.path.exists(result_file):

            messagebox.showwarning(
                "No Results",
                "Run a scan before exporting a report."
            )

            return

        destination = filedialog.asksaveasfilename(
            title="Save Report",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )

        if destination:

            with open(
                result_file,
                "r"
            ) as source:

                contents = source.read()

            with open(
                destination,
                "w"
            ) as output:

                output.write(
                    "DUPLICATE FILE DETECTOR REPORT\n"
                )

                output.write(
                    "====================================\n\n"
                )

                output.write(
                    contents
                )

            messagebox.showinfo(
                "Report Exported",
                "Report saved successfully."
            )


# -------------------------------------------------------------
# MAIN
# -------------------------------------------------------------

if __name__ == "__main__":

    root = tk.Tk()

    app = DuplicateDetectorGUI(
        root
    )

    root.mainloop()