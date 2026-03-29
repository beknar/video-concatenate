"""Video concatenation tool with a tkinter GUI."""

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from moviepy import VideoFileClip, concatenate_videoclips

VIDEO_EXTENSIONS = (
    ".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg",
)


class VideoConcatenatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Video Concatenator")
        self.geometry("620x520")
        self.resizable(False, False)

        self.video_paths: list[str] = []

        self._build_ui()

    # ── UI ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        # --- file list ---
        lbl = tk.Label(self, text="Videos (drag to reorder):", anchor="w")
        lbl.pack(fill="x", padx=10, pady=(10, 2))

        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=10)

        self.listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # drag-to-reorder bindings
        self.listbox.bind("<Button-1>", self._on_drag_start)
        self.listbox.bind("<B1-Motion>", self._on_drag_motion)

        # --- buttons row ---
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=6)

        tk.Button(btn_frame, text="Add Videos", width=12, command=self._add_files).pack(side="left", padx=(0, 4))
        tk.Button(btn_frame, text="Remove Selected", width=14, command=self._remove_selected).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Move Up", width=9, command=self._move_up).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Move Down", width=9, command=self._move_down).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Clear All", width=9, command=self._clear_all).pack(side="left", padx=4)

        # --- output file ---
        out_frame = tk.Frame(self)
        out_frame.pack(fill="x", padx=10, pady=6)

        tk.Label(out_frame, text="Output file:").pack(side="left")
        self.output_var = tk.StringVar(value="output.mp4")
        tk.Entry(out_frame, textvariable=self.output_var, width=36).pack(side="left", padx=6)
        tk.Button(out_frame, text="Browse...", command=self._browse_output).pack(side="left")

        # --- progress ---
        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.pack(fill="x", padx=10, pady=(6, 2))

        self.status_var = tk.StringVar(value="Add at least 2 videos to get started.")
        tk.Label(self, textvariable=self.status_var, anchor="w", fg="gray").pack(fill="x", padx=10)

        # --- concatenate button ---
        self.concat_btn = tk.Button(
            self, text="Concatenate", font=("Segoe UI", 11, "bold"),
            height=2, command=self._start_concatenation,
        )
        self.concat_btn.pack(fill="x", padx=10, pady=(6, 10))

    # ── List helpers ─────────────────────────────────────────────────────
    def _refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for p in self.video_paths:
            self.listbox.insert(tk.END, os.path.basename(p))

    def _add_files(self):
        filetypes = [("Video files", " ".join(f"*{e}" for e in VIDEO_EXTENSIONS)), ("All files", "*.*")]
        paths = filedialog.askopenfilenames(title="Select videos", filetypes=filetypes)
        if paths:
            self.video_paths.extend(paths)
            self._refresh_listbox()
            self.status_var.set(f"{len(self.video_paths)} video(s) in list.")

    def _remove_selected(self):
        sel = self.listbox.curselection()
        if sel:
            del self.video_paths[sel[0]]
            self._refresh_listbox()
            self.status_var.set(f"{len(self.video_paths)} video(s) in list.")

    def _clear_all(self):
        self.video_paths.clear()
        self._refresh_listbox()
        self.status_var.set("List cleared.")

    def _move_up(self):
        sel = self.listbox.curselection()
        if sel and sel[0] > 0:
            i = sel[0]
            self.video_paths[i - 1], self.video_paths[i] = self.video_paths[i], self.video_paths[i - 1]
            self._refresh_listbox()
            self.listbox.selection_set(i - 1)

    def _move_down(self):
        sel = self.listbox.curselection()
        if sel and sel[0] < len(self.video_paths) - 1:
            i = sel[0]
            self.video_paths[i], self.video_paths[i + 1] = self.video_paths[i + 1], self.video_paths[i]
            self._refresh_listbox()
            self.listbox.selection_set(i + 1)

    # ── Drag-to-reorder ─────────────────────────────────────────────────
    def _on_drag_start(self, event):
        self._drag_index = self.listbox.nearest(event.y)

    def _on_drag_motion(self, event):
        target = self.listbox.nearest(event.y)
        if target != self._drag_index:
            self.video_paths[self._drag_index], self.video_paths[target] = (
                self.video_paths[target], self.video_paths[self._drag_index],
            )
            self._refresh_listbox()
            self.listbox.selection_set(target)
            self._drag_index = target

    # ── Output browse ────────────────────────────────────────────────────
    def _browse_output(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 video", "*.mp4")],
            initialfile=self.output_var.get(),
        )
        if path:
            self.output_var.set(path)

    # ── Concatenation ────────────────────────────────────────────────────
    def _start_concatenation(self):
        if len(self.video_paths) < 2:
            messagebox.showwarning("Not enough videos", "Please add at least 2 videos.")
            return

        output = self.output_var.get().strip()
        if not output:
            messagebox.showwarning("No output", "Please specify an output file name.")
            return
        if not output.endswith(".mp4"):
            output += ".mp4"

        self.concat_btn.config(state="disabled")
        self.progress.start(10)
        self.status_var.set("Concatenating...")

        threading.Thread(
            target=self._concatenate_worker,
            args=(list(self.video_paths), output),
            daemon=True,
        ).start()

    def _concatenate_worker(self, paths, output_path):
        clips = []
        try:
            for p in paths:
                self.after(0, self.status_var.set, f"Loading {os.path.basename(p)}...")
                clips.append(VideoFileClip(p))

            self.after(0, self.status_var.set, "Writing output file...")
            final = concatenate_videoclips(clips, method="compose")
            final.write_videofile(output_path, codec="libx264", audio_codec="aac")

            self.after(0, self._on_success, output_path)
        except Exception as exc:
            self.after(0, self._on_error, str(exc))
        finally:
            for c in clips:
                c.close()

    def _on_success(self, output_path):
        self.progress.stop()
        self.concat_btn.config(state="normal")
        self.status_var.set(f"Saved: {output_path}")
        messagebox.showinfo("Done", f"Video saved to:\n{output_path}")

    def _on_error(self, msg):
        self.progress.stop()
        self.concat_btn.config(state="normal")
        self.status_var.set("Error — see details.")
        messagebox.showerror("Error", f"Concatenation failed:\n{msg}")


if __name__ == "__main__":
    app = VideoConcatenatorApp()
    app.mainloop()
