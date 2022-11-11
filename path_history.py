

def path_history(self, path):
        #since paramiko doesnt produce an absolute path, this creates a path
        #history by appending and pop'ing an array as you move through the file
        #structure
        
        if path == '/':
            self.par_dir = '/'
            #self.path = path
            self.path_par_hist = ['/']
            self.path_hist = ['/']
            self.path_depth = 0
        elif path.startswith('/'):
            path = path.lstrip('.')
            self.path_hist.append(path)
            self.path_depth +=1
            self.path_par_hist = list(self.path_hist)
            self.path_par_hist.pop()
            self.par_dir = ''.join(map(str, self.path_par_hist))
        elif path.startswith('.') and len(self.path_hist) > 1:
            self.path_hist.pop(self.path_depth)
            self.path_depth -=1
        else:
            self.par_dir = '/'
            if len(self.path_par_hist) != 1:
                self.path_par_hist.pop()
                self.par_dir = ''.join(map(str, self.path_par_hist))
        self.full_path = ''.join(map(str, self.path_hist))
        return self.full_path.replace('//','/')
