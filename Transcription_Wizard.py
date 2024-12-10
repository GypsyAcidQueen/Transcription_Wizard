import openai
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# Set your OpenAI API key directly in the script
openai.api_key = "YOUR_OPENAI_KEY"

def add_paragraph_breaks(text, model="gpt-4o"):
    """Format the Chinese interview text by adding paragraph breaks and marking questions."""
    prompt = (
        "Please format the following unformatted Chinese interview transcript by adding paragraph breaks where natural. "
        "Detect questions asked by the interviewer, and place each question in its own paragraph. "
        "Mark questions with a '# ' at the beginning of the paragraph in markdown format. "
        "Do not change the content of the text in any way. Only add paragraph breaks and mark questions."
    )

    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error: {e}")
        return None

def translate_paragraphs(paragraph, model="gpt-4o"):
    """Translate a single paragraph and place the English translation below the original Chinese text."""
    prompt = (
        "Please translate the following Chinese paragraph to English. "
        "Place the English translation underneath the original Chinese paragraph."
        "You must reproduce the original Chinese paragraph perfectly, do not alter the original Chinese paragraph in any way."
    )

    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": paragraph}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error: {e}")
        return None

def split_text(text, max_chunk_size=2000):
    """Split the text into chunks of approximately max_chunk_size characters."""
    chunks = []
    current_chunk = []
    current_length = 0

    for paragraph in text.split('\n'):
        paragraph_length = len(paragraph)
        if current_length + paragraph_length > max_chunk_size:
            chunks.append("\n".join(current_chunk))
            current_chunk = [paragraph]
            current_length = paragraph_length
        else:
            current_chunk.append(paragraph)
            current_length += paragraph_length

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks

def process_formatting(input_path, formatted_path):
    """Process the input document to format the text and save to an intermediate file."""
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print("Splitting text into chunks for formatting...")
    chunks = split_text(content)

    formatted_chunks = []
    for idx, chunk in enumerate(chunks):
        print(f"Formatting chunk {idx + 1}/{len(chunks)}...")
        formatted_chunk = add_paragraph_breaks(chunk)
        if formatted_chunk:
            formatted_chunks.append(formatted_chunk)
        else:
            messagebox.showerror("Error", f"Failed to format chunk {idx + 1}")
            return

    formatted_text = "\n".join(formatted_chunks)

    with open(formatted_path, 'w', encoding='utf-8') as f:
        f.write(formatted_text)
    messagebox.showinfo("Success", f"Formatting complete! Saved to {formatted_path}")

def process_translation(formatted_path, output_path):
    """Translate the formatted document paragraph by paragraph and save the final output with translations."""
    with open(formatted_path, 'r', encoding='utf-8') as f:
        formatted_content = f.read()

    paragraphs = formatted_content.split('\n')
    translated_paragraphs = []

    for idx, paragraph in enumerate(paragraphs):
        if paragraph.strip():  # Only process non-empty paragraphs
            print(f"Translating paragraph {idx + 1}/{len(paragraphs)}...")
            translated_paragraph = translate_paragraphs(paragraph)
            if translated_paragraph:
                translated_paragraphs.append(paragraph)
                translated_paragraphs.append(translated_paragraph)
                translated_paragraphs.append("")  # Add a blank line for separation
            else:
                messagebox.showerror("Error", f"Failed to translate paragraph {idx + 1}")
                return

    final_translated_text = "\n".join(translated_paragraphs)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_translated_text)

    # Delete the intermediate formatted file
    try:
        os.remove(formatted_path)
        print(f"Deleted intermediate file: {formatted_path}")
    except Exception as e:
        print(f"Error deleting intermediate file: {e}")

    messagebox.showinfo("Success", f"Translation complete! Saved to {output_path}")

def select_input_file():
    """Open a file dialog to select the input file and generate default output paths."""
    file_path = filedialog.askopenfilename(filetypes=[("Markdown files", "*.md")])
    input_file_entry.delete(0, tk.END)
    input_file_entry.insert(0, file_path)

    if file_path:
        base_name, ext = os.path.splitext(file_path)
        intermediate_path = f"{base_name} intermediate{ext}"
        translated_path = f"{base_name} Transcript{ext}"
        intermediate_file_entry.delete(0, tk.END)
        intermediate_file_entry.insert(0, intermediate_path)
        translated_file_entry.delete(0, tk.END)
        translated_file_entry.insert(0, translated_path)

def start_processing():
    """Start the process of formatting and translating the document."""
    input_path = input_file_entry.get()
    formatted_path = intermediate_file_entry.get()
    output_path = translated_file_entry.get()

    if not input_path or not formatted_path or not output_path:
        messagebox.showwarning("Input Error", "Please provide all file paths.")
        return

    process_formatting(input_path, formatted_path)
    process_translation(formatted_path, output_path)

# GUI Setup
root = tk.Tk()
root.title("Chinese Interview Formatter and Translator with GPT")

# Input File Selection
tk.Label(root, text="Select Input Markdown File:").pack(pady=5)
input_file_frame = tk.Frame(root)
input_file_frame.pack(pady=5)
input_file_entry = tk.Entry(input_file_frame, width=50)
input_file_entry.pack(side=tk.LEFT, padx=5)
select_file_button = ttk.Button(input_file_frame, text="Browse", command=select_input_file)
select_file_button.pack(side=tk.LEFT)

# Intermediate File Display
tk.Label(root, text="Intermediate File Path:").pack(pady=5)
intermediate_file_entry = tk.Entry(root, width=60)
intermediate_file_entry.pack(pady=5)

# Final Translated File Display
tk.Label(root, text="Final Translated File Path:").pack(pady=5)
translated_file_entry = tk.Entry(root, width=60)
translated_file_entry.pack(pady=5)

# Start Button
start_button = ttk.Button(root, text="Format and Translate Interview Markdown", command=start_processing)
start_button.pack(pady=20)

# Run the GUI loop
root.mainloop()
