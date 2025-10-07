from the_west_inner.requests_handler import requests_handler




class Notebook:
    
    def __init__(self , handler : requests_handler):
        self.handler = handler
        self._content : str | None = None
    
    def _read_notebook(self ) -> str:
        
        response = self.handler.post(
            window = 'character',
            action= 'get_notebook',
            action_name= 'ajax'
        )
        
        return response.get('raw')
    
    @property
    def content(self) -> str:
        
        if self._content is None:
            
            self._content = self._read_notebook()
        
        return self._content
    def reset_content(self):
        self._content = None
        
    def _save_edit(self , new_text : str) :
        
        response = self.handler.post(
            window = 'character',
            action= 'save_notebook',
            payload= {'notebook' : new_text},
            use_h= True
        )
        
        return response
    
    def edit(self , new_text : str) :
        
        self._save_edit(new_text= new_text)
        
        self._content = new_text