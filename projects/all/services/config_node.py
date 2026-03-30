class ConfigNode:
    def __init__(self, obj):
        self.conv_recursive(obj)

    def conv_recursive(self, obj):
        if obj is not None:
            for k, v in obj.items():
                if type(v) is dict:
                    setattr(self, k, ConfigNode(v))
                else:
                    setattr(self, k, v)