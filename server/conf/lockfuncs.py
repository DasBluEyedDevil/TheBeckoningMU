"""
Custom lock functions for beckonmu.

Lock functions are callables that receive an accessing object,
an accessed object, and a string denoting what kind of access is
attempted.

Lock functions should return True if access is granted, False otherwise.

Example:
    def mylock(accessing_obj, accessed_obj, *args, **kwargs):
        '''
        A simple example lock function.
        '''
        return accessing_obj.id == 1

Usage in locks:
    "examine:mylock()"

"""

# Add your custom lock functions below.
# They will be available for use in lock definitions throughout the game.
