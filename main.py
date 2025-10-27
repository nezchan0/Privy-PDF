import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from pypdf import PdfReader, PdfWriter

def parse_page_ranges(input_str, num_pages):
    """
    Return sorted valid *zero-based* page indices (derived from 1-based user input)
    and a list of error messages for each invalid part.
    """
    pages = set()
    errors = []
    input_str = input_str.replace(" ", "")
    parts = [p for p in input_str.split(",") if p]

    for part in parts:
        # '-N' means pages 1 to N inclusive
        if part.startswith("-") and part[1:].isdigit():
            end = int(part[1:])
            if end < 1:
                errors.append(f"'-{end}' is below 1.")
            elif end > num_pages:
                errors.append(f"'-{end}' ends at {end}, but max page is {num_pages}.")
            else:
                pages.update(range(0, end))
        # 'N-' means pages N to last
        elif part.endswith("-") and part[:-1].isdigit():
            start = int(part[:-1])
            if start < 1:
                errors.append(f"'{start}-' starts below 1.")
            elif start > num_pages:
                errors.append(f"'{start}-' starts at {start}, but max page is {num_pages}.")
            else:
                pages.update(range(start-1, num_pages))
        # ranges 'M-N' means pages M to N inclusive
        elif "-" in part:
            try:
                start_str, end_str = part.split("-", 1)
                start = int(start_str)
                end = int(end_str)
                if start < 1 or end < 1:
                    errors.append(f"'{part}' range contains numbers < 1.")
                elif start > num_pages or end > num_pages:
                    errors.append(f"'{part}' range out of bounds (max page: {num_pages}).")
                elif start > end:
                    errors.append(f"'{part}': start {start} greater than end {end}.")
                else:
                    pages.update(range(start-1, end))
            except ValueError:
                errors.append(f"'{part}' is malformed range.")
        # single pages
        elif part.isdigit():
            idx = int(part)
            if idx < 1:
                errors.append(f"'{idx}' is below 1.")
            elif idx > num_pages:
                errors.append(f"'{idx}' is out of bounds (max page: {num_pages}).")
            else:
                pages.add(idx-1)
        else:
            errors.append(f"'{part}' is not valid (numbers from 1 to {num_pages} only).")
    return sorted(pages), errors

def merge_pdfs():
    files = filedialog.askopenfilenames(
        title="Select PDFs to Merge",
        filetypes=[("PDF Files", "*.pdf")],
    )
    if not files:
        return
    output_name = filedialog.asksaveasfilename(
        title="Save Merged PDF As...",
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf")],
    )
    if not output_name:
        return
    writer = PdfWriter()
    for path in files:
        writer.append(path)
    with open(output_name, "wb") as f_out:
        writer.write(f_out)
    messagebox.showinfo("Success", f"Merged PDF saved as:\n{output_name}")
def delete_pages():
    file = filedialog.askopenfilename(
        title="Select PDF for Page Deletion",
        filetypes=[("PDF Files", "*.pdf")],
    )
    if not file:
        return
    reader = PdfReader(file)
    num_pages = len(reader.pages)
    base_message = (
    f"This file has {num_pages} pages (1 to {num_pages}).\n"
    "Enter pages to REMOVE. Format examples:\n"
    "  - Use dashes for ranges (e.g. 40-65)\n"
    "  - Use '-N' for start to N (e.g. -4 means 1-4)\n"
    "  - Use 'N-' for N to end (e.g. 90- means 90 to end)\n"
    "  - Separate any with commas (e.g. -4,15,19,40-65,90-)"
)


    while True:
        answer = simpledialog.askstring(
            "Pages to Delete",
            base_message,
            parent=root
        )
        if answer is None:
            return  # User cancelled

        to_delete, errors = parse_page_ranges(answer, num_pages)

        if errors:
            err_text = "Invalid input:\n" + "\n".join(errors) + "\nPlease re-enter valid page numbers/ranges."
            messagebox.showerror("Invalid Input", err_text)
            continue  # Loop again

        if not to_delete:
            messagebox.showinfo("No Pages", "No valid pages specified for deletion.")
            continue  # Loop again

        # All okay, proceed
        writer = PdfWriter()
        for i in range(num_pages):
            if i not in to_delete:
                writer.add_page(reader.pages[i])
        output_name = filedialog.asksaveasfilename(
            title="Save Result PDF As...",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
        )
        if not output_name:
            return
        with open(output_name, "wb") as f_out:
            writer.write(f_out)
        messagebox.showinfo("Done", f"PDF saved as:\n{output_name}")
        return

root = tk.Tk()
root.title("Privy-PDF")

tk.Label(root, text="PDF Organizer (Merge, Delete Pages, Custom Output)", font=("Calibri", 14)).pack(pady=10)
tk.Button(root, text="Merge Multiple PDFs", command=merge_pdfs, width=30).pack(pady=8)
tk.Button(root, text="Delete Pages From a PDF", command=delete_pages, width=30).pack(pady=8)
tk.Button(root, text="Exit", command=root.destroy, width=30).pack(pady=8)

root.mainloop()
