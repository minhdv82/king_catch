import math

class Node:
    def __init__(self, value, op=None, children=(), requires_grad=False) -> None:
        self._op = op
        self._children = children
        self.value = value
        self.grad = 0
        self.requires_grad = requires_grad
        self._out_grad = lambda : None

    def backward(self):
        if not self.requires_grad:
            print('This node does not requires grad!')
            return
        nodes = []
        visited = set()
        def _topo_sort(node: Node):
            if node not in visited and node.requires_grad:
                visited.add(node)
                for child in node._children:
                    _topo_sort(child)
                nodes.append(node)
        _topo_sort(self)
        
        self.grad = 1.
        for node in reversed(nodes):
            node._out_grad()

    def __add__(self, other):
        other = other if isinstance(other, Node) else Node(other)
        res = Node(self.value + other.value, '+', (self, other),
                   requires_grad=self.requires_grad or other.requires_grad)

        if res.requires_grad:
            def _out_grad():
                self.grad += res.grad
                other.grad += res.grad

            res._out_grad = _out_grad

        return res
        
    def __sub__(self, other):
        return self + (other * (-1))

    def __mul__(self, other):
        other = other if isinstance(other, Node) else Node(other)
        res = Node(self.value * other.value, '*', (self, other),
                   requires_grad=self.requires_grad or other.requires_grad)

        if res.requires_grad:
            def _out_grad():
                self.grad += res.grad * other.value
                other.grad += res.grad * self.value

            res._out_grad = _out_grad

        return res
    
    def pow(self, n):
        res = Node(self.value**n, 'pow', (self,), requires_grad=self.requires_grad)

        if res.requires_grad:
            def _out_grad():
                self.grad += n * (self.value)**(n - 1.) * res.grad

            res._out_grad = _out_grad

        return res
    
    def sin(self):
        res = Node(math.sin(self.value), 'sin', (self,), requires_grad=self.requires_grad)

        if res.requires_grad:
            def _out_grad():
                self.grad += math.cos(self.value) * res.grad

            res._out_grad = _out_grad

        return res
    
    def cos(self):
        res = Node(math.cos(self.value), 'cos', (self,), requires_grad=self.requires_grad)

        if res.requires_grad:
            def _out_grad():
                self.grad += -math.sin(self.value) * res.grad

            res._out_grad = _out_grad

        return res
    
    def relu(self):
        res = Node((self.value > 0) * self.value, 'relu', (self,), requires_grad=self.requires_grad)

        if res.requires_grad:
            def _out_grad():
                self.grad += (self.value > 0) * res.grad
            
            res._out_grad = _out_grad

        return res