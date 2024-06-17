import os

def process_file(file_path: str) -> str:
    processed_file_path = f"processed_{os.path.basename(file_path)}"
    # Add your processing logic here
    with open(file_path, 'rb') as file:
        content = file.read()
    with open(f"static/{processed_file_path}", 'wb') as file:
        file.write(content)
    return processed_file_path
