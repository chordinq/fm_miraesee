def miraesee_extension(func):
    """
    Marks a method or property as a custom extension for the Miraesee simulator.
    This indicates that the code is not part of the original decompiled C# source, 
    but a helper added for simulation purposes.
    """
    return func