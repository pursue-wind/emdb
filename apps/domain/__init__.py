class MyClass:
    def __init__(self):
        self._prop = 2
        self._another_prop = 0

    @property
    def prop(self):
        print("Accessing prop")
        return self._prop+2


# 示例使用
obj = MyClass()
print(obj.prop)  # 访问 prop，触发监听和自动修改
