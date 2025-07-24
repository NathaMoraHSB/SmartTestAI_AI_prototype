# GUI toolkit
import tkinter as tk
from tkinter import filedialog, messagebox

# URL utilities
from urllib.parse import urlparse

# File system operations
import os
import shutil

# Assistant types (enum)
from infrastructure.gpt.models.assistant_name import AssistantName

# GPT request handler
from infrastructure.gpt.repositories.assistant_gpt_repository import send_request

# File processing functions (PDF, DOCX, spreadsheet, websites)
from infrastructure.gpt.files_intake.vector_db import process_single_pdf, process_all_supported_files_in_folder, \
    process_single_spreadsheet, process_single_docx, process_entire_website, process_single_webpage




#------------------------------Main GUI Application Class----------------------------------------------------------
class AssistantApp:
    def __init__(self, root):

        """
        Initialize the GUI application and layout all interface components.
        """

        self.root = root
        self.root.title("Responses API Test GUI")
        self.root.geometry("1000x900")

        # Store paths of selected image files to send with the request
        self.image_paths = []

        # --- Section: Web URL Input ---
        self.web_label = tk.Label(root, text="Enter website URL:")
        self.web_label.pack(pady=5)

        self.web_entry = tk.Entry(root, width=90)
        self.web_entry.pack(pady=5)

        # Option to process the entire website (sitemap or crawl)
        self.entire_website_var = tk.BooleanVar()
        self.entire_checkbox = tk.Checkbutton(root, text="Process entire website", variable=self.entire_website_var)
        self.entire_checkbox.pack(pady=2)

        self.web_button = tk.Button(root, text="Submit Website", command=self.process_website_from_gui)
        self.web_button.pack(pady=10)

        # --- Section: Upload Files ---
        self.upload_button = tk.Button(root, text="Upload File", command=self.upload_file)
        self.upload_button.pack(pady=5)

        # --- Section: Select Assistant Type ---
        self.assistant_var = tk.StringVar(value=AssistantName.EXPLORATORY_TESTING.value)
        frame = tk.LabelFrame(root, text="Select assistant type")
        frame.pack(fill="x", padx=20, pady=10)
        for assistant in AssistantName:
            tk.Radiobutton(
                frame,
                text=assistant.value,
                variable=self.assistant_var,
                value=assistant.value
            ).pack(anchor="w")

        # --- Section: Attach Images ---
        self.attach_img_button = tk.Button(root, text="Attach Images", command=self.attach_images)
        self.attach_img_button.pack(pady=5)

        # --- Section: Send Prompt ---
        self.label = tk.Label(root, text="Enter a prompt:")
        self.label.pack(pady=10)

        self.input_box = tk.Entry(root, width=90)
        self.input_box.pack(pady=5)

        self.send_button = tk.Button(root, text="Send", command=self.get_response)
        self.send_button.pack(pady=10)

        self.response_box = tk.Text(root, width=90, height=50)
        self.response_box.pack(pady=10)

        # Store the ID of the last assistant response for follow-up messages
        self.response_id = None

#-----------------------------Methods for GUI Actions------------------------------------------------------------

    #Attach Images
    def attach_images(self):
        paths = filedialog.askopenfilenames(
            title="Select one or more images",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if paths:
            self.image_paths = list(paths)
            filenames = "\n".join(os.path.basename(p) for p in self.image_paths)
            messagebox.showinfo("Images Attached", f"Selected images:\n{filenames}")
        else:
            self.image_paths = []

    #Send Prompt to Assistant
    def get_response(self):
        prompt = self.input_box.get().strip()
        assistant_name = AssistantName(self.assistant_var.get())

        print(f"[DEBUG] Prompt: {prompt}")
        print(f"[DEBUG] Assistant: {assistant_name}")
        print(f"[DEBUG] Attached Images: {self.image_paths}")

        # Send the request to the assistant backend
        response_text, response_id = send_request(
            prompt=prompt,
            assistant_name=assistant_name,
            previous_response_id=self.response_id,
            image_paths=self.image_paths 
        )

        # Update the response_id for future interactions
        self.response_id = response_id
        print(f"Stored response_id: {self.response_id}")

        # Clear after sending
        self.image_paths = []

        # Display the response in the output text box
        self.response_box.delete("1.0", tk.END)
        self.response_box.insert(tk.END, response_text)

    #Upload and Process File(s)
    def upload_file(self):
        file_paths = filedialog.askopenfilenames(
            title="Select files",
            filetypes=[
                ("Supported files", "*.pdf *.docx *.csv *.xlsx"),
                ("All files", "*.*")
            ]
        )

        if not file_paths:
            return

        # Ensure local destination folder exists
        project_root = os.path.dirname(os.path.abspath(__file__))
        destination_dir = os.path.join(project_root, "files")
        os.makedirs(destination_dir, exist_ok=True)


        # Track the copied files
        uploaded_files = []

        for file_path in file_paths:
            try:
                filename = os.path.basename(file_path)
                destination_path = os.path.join(destination_dir, filename)
                shutil.copy(file_path, destination_path)
                uploaded_files.append(destination_path)
                print(f"📁 File copied to: {destination_path}")
            except Exception as e:
                messagebox.showerror("Copy Error", f"Could not copy {file_path}:\n{e}")

        if not uploaded_files:
            return

        description = "Uploaded via GUI"

        # Process each file individually with unique project ID
        for i, file_path in enumerate(uploaded_files):
            filename = os.path.basename(file_path)
            project_id = f"gui_project_{i+1:03d}"
            print(f"\n📌 Processing `{filename}` with project_id: {project_id}")

            try:
                ext = os.path.splitext(filename)[1].lower()

                if ext == ".pdf":
                    process_single_pdf(
                        pdf_path=file_path,
                        project_id=project_id,
                        file_type="pdf",
                        description=description
                    )
                elif ext == ".docx":
                    process_single_docx(
                        docx_path=file_path,
                        project_id=project_id,
                        file_type="docx",
                        description=description
                    )
                elif ext in {".csv", ".xlsx"}:
                    process_single_spreadsheet(
                        file_path=file_path,
                        project_id=project_id,
                        file_type="spreadsheet",
                        description=description
                    )
                else:
                    print(f"⚠️ Unsupported file type: {filename}")
            except Exception as e:
                messagebox.showerror("Processing Error", f"Error processing {filename}:\n{e}")
                continue

        messagebox.showinfo("Success", f"Successfully processed {len(uploaded_files)} file(s).")

    #Process a Website (Page or Entire Site)
    def process_website_from_gui(self):
        """
        Process a single web page or an entire website based on user selection.
        """
        url = self.web_entry.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please enter a valid URL.")
            return

        description = "Submitted from GUI"
        project_id = f"web_gui_{urlparse(url).netloc.replace('.', '_')}"

        try:
            if self.entire_website_var.get():
                # Process all reachable pages from sitemap or crawl
                process_entire_website(
                    url=url,
                    project_id=project_id,
                    description=description
                )
            else:
                # Process just a single web page
                process_single_webpage(
                    url=url,
                    project_id=project_id,
                    description=description
                )
            messagebox.showinfo("Success", f"Website processed successfully:\n{url}")
        except Exception as e:
            messagebox.showerror("Processing Error", f"Failed to process the URL:\n{e}")
