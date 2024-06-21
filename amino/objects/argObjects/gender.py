class Gender:
    """
    types of genders
    
    attributes:
    - male
    - female
    - non_binary

    - all (list of all attributes)

    """

    male: int = 1
    female: int = 2
    non_binary: int = 255

    all: list = [male, female, non_binary]