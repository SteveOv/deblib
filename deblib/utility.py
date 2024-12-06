""" Maths helper functions. """
# pylint: disable=no-name-in-module, redefined-builtin

def round_to_nearest(value, nearest=1.):
    """
    Round the passed value to the value nearest to the passed nearest argument. 
    For example round_to_nearest(23.74, 0.5) will return 23.5
    wheras round_to_nearest(23.75, 0.5) will return 24.

    :value: the value to round
    :nearest: the target to round "to the nearest". Defaults to 1.
    """
    if nearest == 1.:
        result = round(value)
    else:
        mod = value % nearest
        result = value - mod
        if mod + mod >= nearest:
            result += nearest
    return result
