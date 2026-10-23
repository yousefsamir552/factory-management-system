import os

output_file = 'all_code.txt'
# تجاهل المجلدات التي لا تحتوي على أكواد الموقع
skip_dirs = {'venv', '.venv', '__pycache__', 'uploads', 'images'}
valid_extensions = {'.py', '.html', '.css', '.js'}

with open(output_file, 'w', encoding='utf-8') as outfile:
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if any(file.endswith(ext) for ext in valid_extensions):
                filepath = os.path.join(root, file)
                outfile.write(f"\n\n{'='*50}\n")
                outfile.write(f"File: {filepath}\n")
                outfile.write(f"{'='*50}\n\n")
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
                    outfile.write(infile.read())
                    
print("تم تجميع الأكواد بنجاح في ملف all_code.txt")