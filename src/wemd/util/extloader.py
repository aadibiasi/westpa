import sys, imp
import logging

log = logging.getLogger(__name__)

def load_module(module_name, path = None):
    """Load and return the given module, recursively loading containing packages as necessary."""
    spec_components = list(reversed(module_name.split('.')))
    qname_components = []
    mod_chain = []
    while spec_components:
        next_component = spec_components.pop(-1)
        qname_components.append(next_component)
        
        try:
            parent = mod_chain[-1]
            path = parent.__path__
        except IndexError:
            parent = None

        # This will raise ImportError if next_component is not found
        # (as one would hope)    
        (fp, pathname, desc) = imp.find_module(next_component, path)
        
        qname = '.'.join(qname_components)
        try:
            module = imp.load_module(qname, fp, pathname, desc)
        finally:
            try:
                fp.close()
            except AttributeError:
                pass
            
        # make the module appear in sys.modules
        sys.modules[qname] = module
        
        # Make the module appear in the parent module's namespace
        if parent:
            setattr(parent, next_component, module)
        
        log.debug('module %r loaded' % qname)

    return module

def get_object(object_name, path=None):
    """Attempt to load the given object, using additional path information if given."""

    try:
        (modspec, symbol) = object_name.rsplit('.', 1)
    except ValueError:
        # no period found
        raise ValueError("object_name name must be in the form 'module.symbol'")
    
    log.debug('attempting to load %r from %r' % (symbol, modspec))
    module = load_module(modspec, path)
    
    # This will raise AttributeError (as expected) if the symbol is not in the module
    return getattr(module, symbol)    

if __name__ == '__main__':
    
    print get_object('numpy.array')
    