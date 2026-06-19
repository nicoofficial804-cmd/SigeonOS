import os
import time

class VirtualFile:
    def __init__(self, name, content="", file_type="txt", location="Home", date=""):
        self.name = name
        self.content = content
        self.file_type = file_type
        self.location = location
        self.date = date

class VirtualFS:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VirtualFS, cls).__new__(cls)
            cls._instance.base_dir = os.path.dirname(os.path.dirname(__file__))
            cls._instance.root_dir = None
            cls._instance.current_user = None
        return cls._instance

    def set_current_user(self, username):
        self.current_user = username
        self.root_dir = os.path.join(self.base_dir, "users", username, "Home")
        os.makedirs(self.root_dir, exist_ok=True)
        
        # Create default folders
        for f in ["Desktop", "Documents", "Downloads", "Pictures", "Music", "Videos", "Projects"]:
            os.makedirs(os.path.join(self.root_dir, f), exist_ok=True)

    def _get_real_path(self, path_list):
        if not path_list:
            return self.root_dir
        if path_list[0] == "Home":
            rel_path = os.path.join(*path_list[1:]) if len(path_list) > 1 else ""
            return os.path.join(self.root_dir, rel_path)
        
        # If it's a real absolute path (like C:\ or /)
        if os.path.isabs(path_list[0]) or (len(path_list[0]) > 1 and path_list[0][1] == ':'):
            return os.path.join(*path_list)
            
        # Fallback
        return os.path.join(self.root_dir, "_dummy")

    def get_node(self, path_list):
        real_path = self._get_real_path(path_list)
        if not os.path.exists(real_path):
            return None
            
        if os.path.isdir(real_path):
            node = {}
            try:
                for name in os.listdir(real_path):
                    item_path = os.path.join(real_path, name)
                    if os.path.isdir(item_path):
                        node[name] = {} # Dict for folder
                    else:
                        ext = name.split('.')[-1].lower() if '.' in name else "file"
                        mtime = os.path.getmtime(item_path)
                        date_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(mtime))
                        
                        content = ""
                        if ext in ["txt", "sgpj"]:
                            try:
                                with open(item_path, "r", encoding="utf-8") as f:
                                    content = f.read()
                            except:
                                content = ""
                        else:
                            content = item_path # store absolute path for photos etc.
                            
                        loc = "/".join(path_list)
                        node[name] = VirtualFile(name, content, ext, loc, date_str)
            except:
                pass
            return node
        else:
            return None
            
    def get_file(self, path_list, filename):
        node = self.get_node(path_list)
        if isinstance(node, dict) and filename in node:
            return node[filename]
        return None
        
    def write_file(self, path_list, filename, content, file_type="txt"):
        real_path = self._get_real_path(path_list)
        os.makedirs(real_path, exist_ok=True)
        file_path = os.path.join(real_path, filename)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except:
            return False

    def delete_file(self, path_list, filename):
        real_path = self._get_real_path(path_list)
        file_path = os.path.join(real_path, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except:
                pass
        return False

    def get_recent_files(self):
        recent = []
        for root, dirs, files in os.walk(self.root_dir):
            for name in files:
                item_path = os.path.join(root, name)
                ext = name.split('.')[-1].lower() if '.' in name else "file"
                mtime = os.path.getmtime(item_path)
                date_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(mtime))
                
                rel = os.path.relpath(root, self.root_dir)
                loc = "Home" if rel == "." else f"Home/{rel.replace(os.sep, '/')}"
                
                content = item_path
                recent.append((mtime, VirtualFile(name, content, ext, loc, date_str)))
        
        # Sort by mtime descending
        recent.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in recent[:15]]
