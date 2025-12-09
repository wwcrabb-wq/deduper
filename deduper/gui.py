"""
GUI implementation for the image deduplication tool.
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
import time
from pathlib import Path
from .deduplicator import Deduplicator


class DeduperGUI:
    """Main GUI window for the image deduplication tool."""
    
    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("Image Deduplication Tool")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Variables
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.similarity_threshold = tk.DoubleVar(value=0.95)
        self.is_processing = False
        self.deduplicator = None
        self.start_time = None
        self.progress_value = 0
        self.progress_total = 100
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        """Create all GUI widgets."""
        # Configure grid weights for responsive layout
        self.root.grid_rowconfigure(6, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(self.root, text="Image Deduplication Tool", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10, padx=10)
        
        # Input folder selection
        ttk.Label(self.root, text="Input Folder:").grid(
            row=1, column=0, sticky="w", padx=10, pady=5)
        ttk.Entry(self.root, textvariable=self.input_folder, width=50).grid(
            row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(self.root, text="Browse...", 
                  command=self.browse_input).grid(
            row=1, column=2, padx=10, pady=5)
        
        # Output folder selection
        ttk.Label(self.root, text="Output Folder:").grid(
            row=2, column=0, sticky="w", padx=10, pady=5)
        ttk.Entry(self.root, textvariable=self.output_folder, width=50).grid(
            row=2, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(self.root, text="Browse...", 
                  command=self.browse_output).grid(
            row=2, column=2, padx=10, pady=5)
        
        # Similarity threshold
        threshold_frame = ttk.Frame(self.root)
        threshold_frame.grid(row=3, column=0, columnspan=3, 
                           sticky="ew", padx=10, pady=10)
        
        ttk.Label(threshold_frame, text="Similarity Threshold:").pack(
            side="left", padx=5)
        
        self.threshold_slider = ttk.Scale(
            threshold_frame, from_=0.5, to=1.0, 
            variable=self.similarity_threshold,
            orient="horizontal", length=300,
            command=self.update_threshold_label)
        self.threshold_slider.pack(side="left", padx=10)
        
        self.threshold_label = ttk.Label(
            threshold_frame, text=f"{self.similarity_threshold.get()*100:.1f}%")
        self.threshold_label.pack(side="left", padx=5)
        
        # Progress bar
        progress_frame = ttk.Frame(self.root)
        progress_frame.grid(row=4, column=0, columnspan=3, 
                          sticky="ew", padx=10, pady=10)
        
        ttk.Label(progress_frame, text="Progress:").pack(
            side="left", padx=5)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame, mode='determinate', length=500)
        self.progress_bar.pack(side="left", padx=10, fill="x", expand=True)
        
        self.eta_label = ttk.Label(progress_frame, text="ETA: --:--")
        self.eta_label.pack(side="left", padx=5)
        
        # Control buttons
        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(
            button_frame, text="Start Deduplication", 
            command=self.start_deduplication, width=20)
        self.start_button.pack(side="left", padx=5)
        
        self.stop_button = ttk.Button(
            button_frame, text="Stop", 
            command=self.stop_deduplication, 
            state="disabled", width=15)
        self.stop_button.pack(side="left", padx=5)
        
        # Status log
        log_frame = ttk.LabelFrame(self.root, text="Status Log", padding=5)
        log_frame.grid(row=6, column=0, columnspan=3, 
                      sticky="nsew", padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, wrap=tk.WORD, height=20)
        self.log_text.pack(fill="both", expand=True)
        
    def browse_input(self):
        """Browse for input folder."""
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.input_folder.set(folder)
            self.log_message(f"Input folder selected: {folder}")
            
    def browse_output(self):
        """Browse for output folder."""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)
            self.log_message(f"Output folder selected: {folder}")
    
    def update_threshold_label(self, value):
        """Update threshold label when slider changes."""
        threshold = float(value)
        self.threshold_label.config(text=f"{threshold*100:.1f}%")
    
    def log_message(self, message):
        """Add a message to the log."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_progress(self, current, total):
        """Update progress bar and ETA."""
        self.progress_value = current
        self.progress_total = total
        
        if total > 0:
            progress_pct = (current / total) * 100
            self.progress_bar['value'] = progress_pct
            
            # Calculate ETA
            if self.start_time and current > 0:
                elapsed = time.time() - self.start_time
                rate = current / elapsed
                remaining = total - current
                eta_seconds = remaining / rate if rate > 0 else 0
                
                if eta_seconds < 60:
                    eta_str = f"ETA: {int(eta_seconds)}s"
                else:
                    minutes = int(eta_seconds // 60)
                    seconds = int(eta_seconds % 60)
                    eta_str = f"ETA: {minutes}m {seconds}s"
                
                self.eta_label.config(text=eta_str)
        
        self.root.update_idletasks()
    
    def start_deduplication(self):
        """Start the deduplication process."""
        # Validate inputs
        input_path = self.input_folder.get()
        output_path = self.output_folder.get()
        
        if not input_path:
            self.log_message("ERROR: Please select an input folder.")
            return
        
        if not output_path:
            self.log_message("ERROR: Please select an output folder.")
            return
        
        if not Path(input_path).exists():
            self.log_message(f"ERROR: Input folder does not exist: {input_path}")
            return
        
        if input_path == output_path:
            self.log_message("ERROR: Input and output folders must be different.")
            return
        
        # Create output folder if it doesn't exist
        Path(output_path).mkdir(parents=True, exist_ok=True)
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        
        # Update UI state
        self.is_processing = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.progress_bar['value'] = 0
        self.eta_label.config(text="ETA: Calculating...")
        self.start_time = time.time()
        
        # Create deduplicator
        self.deduplicator = Deduplicator(
            input_path, output_path, 
            self.similarity_threshold.get())
        
        # Start processing in a separate thread
        thread = threading.Thread(target=self.run_deduplication, daemon=True)
        thread.start()
    
    def run_deduplication(self):
        """Run the deduplication process in a separate thread."""
        try:
            stats = self.deduplicator.deduplicate(
                progress_callback=self.update_progress,
                log_callback=self.log_message)
            
            # Update UI when complete
            self.root.after(0, self.deduplication_complete, stats)
            
        except Exception as e:
            error_msg = f"ERROR: {str(e)}"
            self.root.after(0, self.log_message, error_msg)
            self.root.after(0, self.deduplication_complete, {'error': str(e)})
    
    def deduplication_complete(self, stats):
        """Handle deduplication completion."""
        self.is_processing = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.eta_label.config(text="ETA: --:--")
        
        if not stats.get('stopped') and not stats.get('error'):
            self.progress_bar['value'] = 100
    
    def stop_deduplication(self):
        """Stop the deduplication process."""
        if self.deduplicator:
            self.log_message("\nStopping process...")
            self.deduplicator.stop()
            self.stop_button.config(state="disabled")


def main():
    """Main entry point for the GUI."""
    root = tk.Tk()
    app = DeduperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
