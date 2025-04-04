import os

class ListDir:
    def __init__(self, start_dir=None):
        if start_dir is None:
            start_dir = os.getcwd()  
        self.current_dirpath = start_dir

    def pwd(self):
        print(self.current_dirpath)

    def ls(self):
        try:
            contents = os.listdir(self.current_dirpath)
            contents.sort()  
            for item in contents:
                print(item)
        except Exception as e:
            print(f"Error listing directory contents: {e}")

    def cd(self, path):
        new_path = os.path.join(self.current_dirpath, path)  
        if os.path.isdir(new_path):
            self.current_dirpath = new_path  
        else:
            raise FileNotFoundError(f"No such directory: {path}")


if __name__ == "__main__":
    dir_manager = ListDir()
    dir_manager.pwd()
    dir_manager.ls()  
    dir_manager.cd('..')
    dir_manager.ls()
