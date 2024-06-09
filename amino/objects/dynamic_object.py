
class DynamicObject:
    def __init__(self, data):
        self.__dict__['attributes'] = {}
        self.__dict__['is_list'] = isinstance(data, list)
        self.__dict__['original_data'] = data
        self._populate(data)

    def _populate(self, data):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    value = DynamicObject(value)
                elif isinstance(value, list):
                    value = [DynamicObject(item) if isinstance(item, dict) else item for item in value]
                self.__dict__['attributes'][key] = value
        elif isinstance(data, list):
            self.__dict__['attributes'] = [DynamicObject(item) if isinstance(item, dict) else item for item in data]
        else:
            raise ValueError("Input data must be a dictionary or a list of dictionaries")

    def __getattr__(self, item):
        if 'attributes' in self.__dict__ and not self.__dict__['is_list']:
            if item in self.__dict__['attributes']:
                return self.__dict__['attributes'][item]
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

    def __getitem__(self, index):
        if self.__dict__['is_list']:
            return self.__dict__['attributes'][index]
        elif isinstance(self.__dict__['attributes'], dict):
            return self.__dict__['attributes'][index]
        raise TypeError(f"'{self.__class__.__name__}' object is not subscriptable")

    def __len__(self):
        if self.__dict__['is_list']:
            return len(self.__dict__['attributes'])
        return 0

    def get_original_data(self):
        return self.__dict__['original_data']

    def __repr__(self):
        return self._recursive_repr()

    def _recursive_repr(self, indent=0):
        items = []
        if self.__dict__['is_list']:
            for i, v in enumerate(self.__dict__['attributes']):
                if isinstance(v, DynamicObject):
                    v_repr = v._recursive_repr(indent + 2)
                else:
                    v_repr = repr(v)
                items.append(f"{' ' * indent}[{i}]={v_repr}")
        else:
            for k, v in self.__dict__['attributes'].items():
                if isinstance(v, DynamicObject):
                    v_repr = v._recursive_repr(indent + 2)
                else:
                    v_repr = repr(v)
                items.append(f"{' ' * indent}{k}={v_repr}")
        return "{\n" + ",\n".join(items) + "\n" + ' ' * (indent - 2) + "}"