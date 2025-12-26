import json
import os
import re
import shutil

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEARN_JSON_PATH = os.path.join(BASE_DIR, "data", "learn.json")
LEARN_FOLDER_PATH = os.path.join(BASE_DIR, "data", "learn")

def slugify(name):
    """Convert a name like 'Node.js' to a slug like 'nodejs'"""
    # Convert to lowercase
    slug = name.lower()
    # Replace special characters and spaces with hyphens
    slug = re.sub(r'[.\s]+', '-', slug)
    # Remove any characters that aren't alphanumeric or hyphens
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    return slug

def extract_old_name_from_path(path):
    """Extract the old folder/file name from a path like 'learn/sindresorhus_awesome-nodejs/sindresorhus_awesome-nodejs.html'"""
    if not path or not path.startswith("learn/"):
        return None
    parts = path.split("/")
    if len(parts) >= 2:
        return parts[1]  # Returns 'sindresorhus_awesome-nodejs'
    return None

def collect_all_items(data):
    """Recursively collect all items with name and path from the JSON"""
    items = []
    
    if isinstance(data, dict):
        # Check if this dict has both 'name' and 'path' keys
        if 'name' in data and 'path' in data:
            path = data.get('path', '')
            if path and path.startswith('learn/') and path.endswith('.html'):
                items.append({
                    'name': data['name'],
                    'path': path,
                    'data_ref': data  # Keep reference to update later
                })
        
        # Recursively check all values
        for key, value in data.items():
            items.extend(collect_all_items(value))
    
    elif isinstance(data, list):
        for item in data:
            items.extend(collect_all_items(item))
    
    return items

def get_rename_mapping(items):
    """Create a mapping of old_name -> new_slug, handling duplicates"""
    slug_counts = {}
    mapping = {}  # old_folder_name -> new_slug
    
    for item in items:
        old_name = extract_old_name_from_path(item['path'])
        if not old_name or old_name in mapping:
            continue
        
        new_slug = slugify(item['name'])
        
        # Handle duplicates by adding a number suffix
        if new_slug in slug_counts:
            slug_counts[new_slug] += 1
            final_slug = f"{new_slug}-{slug_counts[new_slug]}"
        else:
            slug_counts[new_slug] = 1
            final_slug = new_slug
        
        mapping[old_name] = final_slug
    
    return mapping

def update_file_content(file_path, old_name, new_name):
    """Replace old_name with new_name in file content"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Replace all occurrences
        updated_content = content.replace(old_name, new_name)
        
        if content != updated_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            return True
        return False
    except Exception as e:
        print(f"  Error updating file {file_path}: {e}")
        return False

def rename_folder_and_files(old_folder_name, new_folder_name):
    """Rename folder and files inside it"""
    old_folder_path = os.path.join(LEARN_FOLDER_PATH, old_folder_name)
    new_folder_path = os.path.join(LEARN_FOLDER_PATH, new_folder_name)
    
    if not os.path.exists(old_folder_path):
        print(f"  Folder not found: {old_folder_path}")
        return False
    
    if os.path.exists(new_folder_path):
        print(f"  Target folder already exists: {new_folder_path}")
        return False
    
    try:
        # First, rename files inside the folder
        for filename in os.listdir(old_folder_path):
            old_file_path = os.path.join(old_folder_path, filename)
            
            if os.path.isfile(old_file_path):
                # Replace old folder name with new name in filename
                new_filename = filename.replace(old_folder_name, new_folder_name)
                new_file_path = os.path.join(old_folder_path, new_filename)
                
                if old_file_path != new_file_path:
                    os.rename(old_file_path, new_file_path)
                    print(f"  Renamed file: {filename} -> {new_filename}")
                
                # Update content inside the file
                update_file_content(new_file_path, old_folder_name, new_folder_name)
        
        # Then rename the folder itself
        os.rename(old_folder_path, new_folder_path)
        print(f"  Renamed folder: {old_folder_name} -> {new_folder_name}")
        return True
        
    except Exception as e:
        print(f"  Error renaming {old_folder_name}: {e}")
        return False

def update_json_paths(data, mapping):
    """Recursively update all paths in the JSON data"""
    if isinstance(data, dict):
        if 'path' in data and isinstance(data['path'], str):
            path = data['path']
            for old_name, new_name in mapping.items():
                if old_name in path:
                    data['path'] = path.replace(old_name, new_name)
                    break
        
        for key, value in data.items():
            update_json_paths(value, mapping)
    
    elif isinstance(data, list):
        for item in data:
            update_json_paths(item, mapping)

def main():
    print("=" * 60)
    print("Learn Resources Renaming Script")
    print("=" * 60)
    
    # Load JSON
    print("\n[1] Loading learn.json...")
    with open(LEARN_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Collect all items
    print("[2] Collecting all items with paths...")
    items = collect_all_items(data)
    print(f"    Found {len(items)} items with learn paths")
    
    # Create rename mapping
    print("[3] Creating rename mapping...")
    mapping = get_rename_mapping(items)
    print(f"    Created mapping for {len(mapping)} unique folders")
    
    # Preview changes
    print("\n[4] Preview of changes (first 20):")
    print("-" * 60)
    for i, (old_name, new_name) in enumerate(list(mapping.items())[:20]):
        print(f"    {old_name}")
        print(f"    -> {new_name}")
        print()
    
    if len(mapping) > 20:
        print(f"    ... and {len(mapping) - 20} more")
    
    # Ask for confirmation
    print("\n" + "=" * 60)
    response = input("Do you want to proceed with renaming? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("Operation cancelled.")
        return
    
    # Perform renames
    print("\n[5] Renaming folders and files...")
    success_count = 0
    fail_count = 0
    
    for old_name, new_name in mapping.items():
        print(f"\nProcessing: {old_name}")
        if rename_folder_and_files(old_name, new_name):
            success_count += 1
        else:
            fail_count += 1
    
    print(f"\n    Successful: {success_count}, Failed: {fail_count}")
    
    # Update JSON
    print("\n[6] Updating learn.json paths...")
    update_json_paths(data, mapping)
    
    # Save updated JSON
    print("[7] Saving updated learn.json...")
    with open(LEARN_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("DONE! All resources have been renamed.")
    print("=" * 60)

if __name__ == "__main__":
    main()
