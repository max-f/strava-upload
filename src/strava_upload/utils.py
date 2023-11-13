import pickle

TOKEN_FILE = "/tmp/client.pkl"


def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)


def load_object(filename):
    with open(filename, 'rb') as file:
        loaded_object = pickle.load(file)
        return loaded_object
