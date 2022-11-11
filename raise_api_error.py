class RaiseAPIError:
    """captures specified exception and raise ApiErrorCode instead    :raises: AttributeError if code_name is not valid
    """
    def __init__(self, captures, code_name):
        self.captures = captures
        self.code = getattr(error_codes, code_name)    
    def __enter__(self):
            return self    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return False        
        if exc_type == self.captures:
            raise self.code from exc_val
        return False