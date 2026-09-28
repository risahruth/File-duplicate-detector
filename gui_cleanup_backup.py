import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import shutil


class DuplicateDetectorGUI:

    def __init__(self, root):
        self.root = root

        self.root.title("Duplicate File Detector")
        self.root.geometry("1150x800")
        self.root.minsize(950, 700)

        self.root.configure(bg="#f4f1f8")

        self.directory = ""
        self.all_results = []

        # Stores paths selected for cleanup
        self.selected_files = set()

        self.create_styles()
        self.create_header()
        self.create_scan_section()
        self.create_statistics()
        self.create_filter_section()
        self.create_results_section()
        self.create_cleanup_section()
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
            pady=15
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

        self.scan_button.pack(pady=12)

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
            pady=(10, 2)
        )

        value_label = tk.Label(
            card,
            text=value,
            bg="white",
            fg="#6c5b7b",
            font=("Arial", 18, "bold")
        )

        value_label.pack(
            pady=(0, 10)
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
            pady=(12, 5)
        )

        search_label = tk.Label(
            frame,
            text="Search:",
            bg="#f4f1f8",
            fg="#333333",
            font=("Arial", 10, "bold")
        )

        search_label.pack(
            side="left",
            padx=(0, 8)
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
            pady=10
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
            pady=(0, 6)
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
            "select",
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
            "select",
            text="Select"
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
            "select",
            width=70,
            anchor="center"
        )

        self.tree.column(
            "group",
            width=65,
            anchor="center"
        )

        self.tree.column(
            "file",
            width=600
        )

        self.tree.column(
            "type",
            width=110,
            anchor="center"
        )

        self.tree.column(
            "size",
            width=110,
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

        # Double-click a row to select/deselect it
        self.tree.bind(
            "<Double-1>",
            self.toggle_selection
        )

        # Single click also allows selection
        self.tree.bind(
            "<ButtonRelease-1>",
            self.handle_tree_click
        )

    # ---------------------------------------------------------
    # CLEANUP SECTION
    # ---------------------------------------------------------

    def create_cleanup_section(self):

        frame = tk.Frame(
            self.root,
            bg="#f4f1f8"
        )

        frame.pack(
            fill="x",
            padx=30,
            pady=(5, 8)
        )

        self.selection_label = tk.Label(
            frame,
            text="Selected: 0 files",
            bg="#f4f1f8",
            fg="#666666",
            font=("Arial", 9, "bold")
        )

        self.selection_label.pack(
            side="left"
        )

        select_button = tk.Button(
            frame,
            text="Select All Visible",
            command=self.select_all_visible,
            bg="#d9c8e8",
            fg="#333333",
            font=("Arial", 9, "bold"),
            relief="flat",
            padx=12,
            pady=7,
            cursor="hand2"
        )

        select_button.pack(
            side="right",
            padx=(8, 0)
        )

        clear_selection_button = tk.Button(
            frame,
            text="Clear Selection",
            command=self.clear_selection,
            bg="#d9c8e8",
            fg="#333333",
            font=("Arial", 9, "bold"),
            relief="flat",
            padx=12,
            pady=7,
            cursor="hand2"
        )

        clear_selection_button.pack(
            side="right",
            padx=(8, 0)
        )

        cleanup_button = tk.Button(
            frame,
            text="Move Selected to Duplicate_Trash",
            command=self.move_selected_to_trash,
            bg="#6c5b7b",
            fg="white",
            font=("Arial", 9, "bold"),
            relief="flat",
            padx=15,
            pady=7,
            cursor="hand2"
        )

        cleanup_button.pack(
            side="right"
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
            pady=(0, 15)
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

        self.directory = os.path.abspath(
            directory
        )

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

            # Clear previous selections
            self.selected_files.clear()

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

                self.all_results.append(
                    {
                        "group": current_group,
                        "file": path,
                        "type": file_type,
                        "size": current_size
                    }
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
        self.update_selection_label()

    # ---------------------------------------------------------
    # FILE TYPE
    # ---------------------------------------------------------

    def get_file_type(self, path):

        extension = os.path.splitext(
            path
        )[1].lower()

        image_extensions = {
            ".jpg", ".jpeg", ".png",
            ".gif", ".bmp", ".webp",
            ".svg", ".tiff"
        }

        document_extensions = {
            ".txt", ".pdf", ".doc",
            ".docx", ".xls", ".xlsx",
            ".ppt", ".pptx", ".csv",
            ".odt"
        }

        video_extensions = {
            ".mp4", ".mkv", ".avi",
            ".mov", ".wmv", ".flv",
            ".webm"
        }

        audio_extensions = {
            ".mp3", ".wav", ".aac",
            ".flac", ".ogg", ".m4a"
        }

        archive_extensions = {
            ".zip", ".tar", ".gz",
            ".bz2", ".7z", ".rar"
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

            selected = (
                "✓"
                if item["file"] in self.selected_files
                else "☐"
            )

            self.tree.insert(
                "",
                "end",
                values=(
                    selected,
                    item["group"],
                    item["file"],
                    item["type"],
                    item["size"]
                )
            )

    # ---------------------------------------------------------
    # TREE CLICK
    # ---------------------------------------------------------

    def handle_tree_click(self, event):

        item_id = self.tree.identify_row(
            event.y
        )

        column = self.tree.identify_column(
            event.x
        )

        # Only toggle when Select column is clicked
        if item_id and column == "#1":

            self.toggle_item_selection(
                item_id
            )

    # ---------------------------------------------------------
    # TOGGLE SELECTION
    # ---------------------------------------------------------

    def toggle_selection(self, event):

        item_id = self.tree.identify_row(
            event.y
        )

        if item_id:

            self.toggle_item_selection(
                item_id
            )

    def toggle_item_selection(self, item_id):

        values = self.tree.item(
            item_id,
            "values"
        )

        if not values:
            return

        file_path = values[2]

        if file_path in self.selected_files:

            self.selected_files.remove(
                file_path
            )

        else:

            self.selected_files.add(
                file_path
            )

        self.display_current_view()
        self.update_selection_label()

    # ---------------------------------------------------------
    # CURRENT FILTERED VIEW
    # ---------------------------------------------------------

    def get_filtered_results(self):

        search_text = (
            self.search_entry.get()
            .lower()
            .strip()
        )

        selected_type = (
            self.type_filter.get()
        )

        filtered = []

        for item in self.all_results:

            path_match = (
                search_text == ""
                or search_text in item["file"].lower()
            )

            type_match = True

            if selected_type == "Images":
                type_match = (
                    item["type"] == "Image"
                )

            elif selected_type == "Documents":
                type_match = (
                    item["type"] == "Document"
                )

            elif selected_type == "Videos":
                type_match = (
                    item["type"] == "Video"
                )

            elif selected_type == "Audio":
                type_match = (
                    item["type"] == "Audio"
                )

            elif selected_type == "Archives":
                type_match = (
                    item["type"] == "Archive"
                )

            elif selected_type == "Other":
                type_match = item["type"] in {
                    "Other",
                    "No Extension"
                }

            if path_match and type_match:

                filtered.append(
                    item
                )

        return filtered

    def display_current_view(self):

        filtered = self.get_filtered_results()

        self.display_results(
            filtered
        )

    # ---------------------------------------------------------
    # FILTER
    # ---------------------------------------------------------

    def filter_results(self, event=None):

        self.display_current_view()

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

        self.display_current_view()

    # ---------------------------------------------------------
    # SELECT ALL VISIBLE
    # ---------------------------------------------------------

    def select_all_visible(self):

        filtered = self.get_filtered_results()

        for item in filtered:

            self.selected_files.add(
                item["file"]
            )

        self.display_current_view()
        self.update_selection_label()

    # ---------------------------------------------------------
    # CLEAR SELECTION
    # ---------------------------------------------------------

    def clear_selection(self):

        self.selected_files.clear()

        self.display_current_view()
        self.update_selection_label()

    # ---------------------------------------------------------
    # SELECTION COUNT
    # ---------------------------------------------------------

    def update_selection_label(self):

        count = len(
            self.selected_files
        )

        self.selection_label.config(
            text=f"Selected: {count} files"
        )

    # ---------------------------------------------------------
    # MOVE TO DUPLICATE TRASH
    # ---------------------------------------------------------

    def move_selected_to_trash(self):

        if not self.selected_files:

            messagebox.showwarning(
                "No Files Selected",
                "Please select duplicate files first."
            )

            return

        if not self.directory:

            messagebox.showerror(
                "No Directory",
                "Please scan a directory first."
            )

            return

        count = len(
            self.selected_files
        )

        confirmation = messagebox.askyesno(
            "Confirm Safe Cleanup",
            f"You selected {count} file(s).\n\n"
            "The files will NOT be permanently deleted.\n\n"
            "They will be moved to:\n"
            "Duplicate_Trash\n\n"
            "Do you want to continue?"
        )

        if not confirmation:
            return

        trash_directory = os.path.join(
            self.directory,
            "Duplicate_Trash"
        )

        try:

            os.makedirs(
                trash_directory,
                exist_ok=True
            )

            moved_count = 0
            failed_files = []

            for file_path in list(
                self.selected_files
            ):

                if not os.path.isfile(
                    file_path
                ):

                    failed_files.append(
                        file_path
                    )

                    continue

                destination = self.get_unique_destination(
                    trash_directory,
                    file_path
                )

                try:

                    shutil.move(
                        file_path,
                        destination
                    )

                    moved_count += 1

                except Exception:

                    failed_files.append(
                        file_path
                    )

            self.selected_files.clear()

            # Run another scan so the GUI reflects
            # the current state of the directory.
            self.scan()

            if failed_files:

                messagebox.showwarning(
                    "Cleanup Completed",
                    f"Moved {moved_count} file(s).\n\n"
                    f"{len(failed_files)} file(s) could not be moved."
                )

            else:

                messagebox.showinfo(
                    "Cleanup Completed",
                    f"Successfully moved {moved_count} "
                    "file(s) to Duplicate_Trash."
                )

        except Exception as error:

            messagebox.showerror(
                "Cleanup Error",
                str(error)
            )

    # ---------------------------------------------------------
    # UNIQUE DESTINATION
    # ---------------------------------------------------------

    def get_unique_destination(
        self,
        trash_directory,
        original_path
    ):

        filename = os.path.basename(
            original_path
        )

        destination = os.path.join(
            trash_directory,
            filename
        )

        if not os.path.exists(
            destination
        ):

            return destination

        base, extension = os.path.splitext(
            filename
        )

        counter = 1

        while True:

            new_filename = (
                f"{base}_duplicate_{counter}"
                f"{extension}"
            )

            destination = os.path.join(
                trash_directory,
                new_filename
            )

            if not os.path.exists(
                destination
            ):

                return destination

            counter += 1

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

            return (
                f"{size / (1024 * 1024 * 1024):.2f} GB"
            )

        elif size >= 1024 * 1024:

            return (
                f"{size / (1024 * 1024):.2f} MB"
            )

        elif size >= 1024:

            return (
                f"{size / 1024:.2f} KB"
            )

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

        if not os.path.exists(
            result_file
        ):

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