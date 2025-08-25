import inspect
from concurrent.futures import ThreadPoolExecutor, as_completed

class Stack:
    def __init__(self):
        self.input_value = None
        self.nodes = {}        # name -> function
        self.dependencies = {} # name -> arg names
        self.results = {}      # name -> result

    def add(self, func, name=None):
        """Add a function node to the stack.
        - func should take (input, and/or other node names) as arguments.
        - name defaults to the function name.
        """
        if name is None:
            name = func.__name__

        sig = inspect.signature(func)
        deps = list(sig.parameters.keys())

        self.nodes[name] = func
        self.dependencies[name] = deps
        return name

    def run(self):
        """Execute the stack with threading (branches run simultaneously)."""
        with ThreadPoolExecutor() as executor:
            futures = {}

            for name, func in self.nodes.items():
                def task(func=func, name=name):
                    args = []
                    for dep in self.dependencies[name]:
                        if dep == "x":
                            args.append(self.input_value)
                        elif dep in self.results:
                            args.append(self.results[dep])
                        else:
                            raise ValueError(f"Missing dependency: {dep}")
                    result = func(*args)
                    self.results[name] = result
                    return name, result

                futures[executor.submit(task)] = name

            for future in as_completed(futures):
                name, result = future.result()
        return self.results
