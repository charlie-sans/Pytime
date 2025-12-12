"""
Instruction execution engine for ObjectIR runtime
"""

import importlib
import re
from typing import Dict, List, Optional
from oir_types import Value, ValueType
from oir_frame import ExecutionFrame
from Config import PRELOADED_STD_LIB_MODULES


class StandardLibrary:
    """Loads configured modules and exposes their namespaces to the executor."""

    def __init__(self, module_names: List[str]):
        self._modules: Dict[str, object] = {}
        self._namespaces: Dict[str, object] = {}
        self._load_modules(module_names)

    def _load_modules(self, module_names: List[str]) -> None:
        for module_name in module_names:
            try:
                module = importlib.import_module(module_name)
            except ImportError as exc:
                print(f"Warning: unable to load stdlib module '{module_name}': {exc}")
                continue

            self._modules[module_name] = module
            namespaces = getattr(module, "__namespaces__", [module_name])
            for namespace in namespaces:
                self._namespaces[namespace] = module

    def resolve(self, qualified_name: str) -> Optional[object]:
        """Resolve a dotted name to the corresponding object from the stdlib."""

        parts = qualified_name.split(".")
        if not parts:
            return None

        namespace = parts[0]
        target = self._namespaces.get(namespace)
        if target is None:
            return None

        for segment in parts[1:]:
            target = getattr(target, segment, None)
            if target is None:
                return None

        return target


class InstructionExecutor:
    """Executes ObjectIR instructions"""
    
    def __init__(self):
        self.console_output = []
        self.stdlib = StandardLibrary(PRELOADED_STD_LIB_MODULES)
    
    def execute_instruction(self, frame: ExecutionFrame, instruction: str) -> None:
        """Execute a single instruction"""
        parts = instruction.split()
        if not parts:
            return
        
        opcode = parts[0]
        
        # Load instructions
        if opcode == 'ldstr':
            self._ldstr(frame, instruction)
        elif opcode == 'ldc.i4':
            self._ldc_i4(frame, parts)
        elif opcode == 'ldc.i8':
            self._ldc_i8(frame, parts)
        elif opcode == 'ldc.r8':
            self._ldc_r8(frame, parts)
        elif opcode == 'ldnull':
            self._ldnull(frame)
        elif opcode == 'ldc.b.0':
            self._ldc_bool(frame, False)
        elif opcode == 'ldc.b.1':
            self._ldc_bool(frame, True)
        elif opcode == 'ldloc':
            self._ldloc(frame, parts)
        
        # Store instructions
        elif opcode == 'stloc':
            self._stloc(frame, parts)
        
        # Arithmetic
        elif opcode == 'add':
            self._add(frame)
        elif opcode == 'sub':
            self._sub(frame)
        elif opcode == 'mul':
            self._mul(frame)
        elif opcode == 'div':
            self._div(frame)
        elif opcode == 'rem':
            self._rem(frame)
        
        # Comparison
        elif opcode == 'ceq':
            self._ceq(frame)
        elif opcode == 'cgt':
            self._cgt(frame)
        elif opcode == 'clt':
            self._clt(frame)
        elif opcode == 'cge':
            self._cge(frame)
        elif opcode == 'cle':
            self._cle(frame)
        
        # Stack manipulation
        elif opcode == 'dup':
            self._dup(frame)
        elif opcode == 'pop':
            self._pop(frame)

        elif opcode == 'if':
            pass  # Control flow instructions are handled at a higher level
        
        # Built-in method calls
        elif opcode == 'call':
            self._call(frame, instruction)
        
        # Return
        elif opcode == 'ret':
            self._ret(frame)
        
        else:
            print(f"Warning: Unknown opcode '{opcode}'")
    
    # Load instruction implementations
    def _ldstr(self, frame: ExecutionFrame, instruction: str) -> None:
        """Load string constant"""
        match = re.search(r'ldstr\s+"([^"]*)"', instruction)
        if match:
            value = Value(match.group(1), ValueType.STRING)
            frame.push(value)
    
    def _ldc_i4(self, frame: ExecutionFrame, parts: list) -> None:
        """Load 32-bit integer constant"""
        value_str = ' '.join(parts[1:])
        value = Value(int(value_str), ValueType.INT32)
        frame.push(value)
    
    def _ldc_i8(self, frame: ExecutionFrame, parts: list) -> None:
        """Load 64-bit integer constant"""
        value_str = ' '.join(parts[1:])
        value = Value(int(value_str), ValueType.INT64)
        frame.push(value)
    
    def _ldc_r8(self, frame: ExecutionFrame, parts: list) -> None:
        """Load double constant"""
        value_str = ' '.join(parts[1:])
        value = Value(float(value_str), ValueType.DOUBLE)
        frame.push(value)
    
    def _ldnull(self, frame: ExecutionFrame) -> None:
        """Load null reference"""
        value = Value(None, ValueType.OBJECT)
        frame.push(value)
    
    def _ldc_bool(self, frame: ExecutionFrame, bool_val: bool) -> None:
        """Load boolean constant"""
        value = Value(bool_val, ValueType.BOOL)
        frame.push(value)
    
    def _ldloc(self, frame: ExecutionFrame, parts: list) -> None:
        """Load local variable"""
        var_name = parts[1]
        value = frame.get_local(var_name)
        frame.push(value)
    
    # Store instruction implementations
    def _stloc(self, frame: ExecutionFrame, parts: list) -> None:
        """Store to local variable"""
        var_name = parts[1]
        value = frame.pop()
        frame.set_local(var_name, value)
    
    # Arithmetic implementations
    def _add(self, frame: ExecutionFrame) -> None:
        """Add two values"""
        b = frame.pop()
        a = frame.pop()
        result = a.data + b.data
        frame.push(Value(result, a.type_))
    
    def _sub(self, frame: ExecutionFrame) -> None:
        """Subtract two values"""
        b = frame.pop()
        a = frame.pop()
        result = a.data - b.data
        frame.push(Value(result, a.type_))
    
    def _mul(self, frame: ExecutionFrame) -> None:
        """Multiply two values"""
        b = frame.pop()
        a = frame.pop()
        result = a.data * b.data
        frame.push(Value(result, a.type_))
    
    def _div(self, frame: ExecutionFrame) -> None:
        """Divide two values"""
        b = frame.pop()
        a = frame.pop()
        result = a.data // b.data if a.type_ in [ValueType.INT32, ValueType.INT64] else a.data / b.data
        frame.push(Value(result, a.type_))
    
    def _rem(self, frame: ExecutionFrame) -> None:
        """Remainder operation"""
        b = frame.pop()
        a = frame.pop()
        result = a.data % b.data
        frame.push(Value(result, a.type_))
    
    # Comparison implementations
    def _ceq(self, frame: ExecutionFrame) -> None:
        """Compare equal"""
        b = frame.pop()
        a = frame.pop()
        result = a.data == b.data
        frame.push(Value(result, ValueType.BOOL))
    
    def _cgt(self, frame: ExecutionFrame) -> None:
        """Compare greater than"""
        b = frame.pop()
        a = frame.pop()
        result = a.data > b.data
        frame.push(Value(result, ValueType.BOOL))
    
    def _clt(self, frame: ExecutionFrame) -> None:
        """Compare less than"""
        b = frame.pop()
        a = frame.pop()
        result = a.data < b.data
        frame.push(Value(result, ValueType.BOOL))
    
    def _cge(self, frame: ExecutionFrame) -> None:
        """Compare greater than or equal"""
        b = frame.pop()
        a = frame.pop()
        result = a.data >= b.data
        frame.push(Value(result, ValueType.BOOL))
    
    def _cle(self, frame: ExecutionFrame) -> None:
        """Compare less than or equal"""
        b = frame.pop()
        a = frame.pop()
        result = a.data <= b.data
        frame.push(Value(result, ValueType.BOOL))
    
    # Stack manipulation implementations
    def _dup(self, frame: ExecutionFrame) -> None:
        """Duplicate top of stack"""
        value = frame.peek()
        frame.push(value)
    
    def _pop(self, frame: ExecutionFrame) -> None:
        """Pop value from stack"""
        frame.pop()
    
    # Call implementations
    def _call(self, frame: ExecutionFrame, instruction: str) -> None:
        """Handle method calls by dispatching to the standard library."""
        match = re.search(r'call\s+([\w\.]+)\s*\(([^)]*)\)\s*(?:->\s*([\w\.]+))?', instruction)
        if not match:
            return

        method_name = match.group(1)
        param_list = match.group(2) or ""
        return_type = match.group(3)
        param_types = [item.strip() for item in param_list.split(',') if item.strip()]
        argument_values = self._pop_call_arguments(frame, len(param_types))

        target_callable = self.stdlib.resolve(method_name)
        if target_callable is None or not callable(target_callable):
            print(f"Warning: unable to resolve call target '{method_name}'")
            return

        python_args = [value.data for value in argument_values]
        if method_name == "System.Console.WriteLine" and python_args:
            self.console_output.append(str(python_args[0]))

        result = target_callable(*python_args)
        self._push_return_value(frame, result, return_type)

    def _pop_call_arguments(self, frame: ExecutionFrame, count: int) -> List[Value]:
        """Pop the required number of arguments from the evaluation stack."""
        values: List[Value] = []
        for _ in range(count):
            values.append(frame.pop())
        values.reverse()
        return values

    def _push_return_value(self, frame: ExecutionFrame, result: object, return_type: Optional[str]) -> None:
        """Wrap the return value in a Value and push it unless the return type is void."""
        if not return_type:
            if isinstance(result, Value):
                frame.push(result)
            elif result is not None:
                frame.push(Value(result, ValueType.OBJECT))
            return

        normalized_return_type = return_type.strip().lower()
        if normalized_return_type in {"void", "system.void"}:
            return

        if isinstance(result, Value):
            frame.push(result)
            return

        frame.push(Value(result, self._resolve_value_type(normalized_return_type)))

    def _resolve_value_type(self, type_name: str) -> ValueType:
        """Normalize a type string to a ValueType."""
        normalized = type_name.strip().lower()
        if normalized.startswith("system."):
            normalized = normalized.split(".", 1)[1]

        return {
            "int32": ValueType.INT32,
            "int64": ValueType.INT64,
            "float": ValueType.FLOAT,
            "double": ValueType.DOUBLE,
            "string": ValueType.STRING,
            "bool": ValueType.BOOL,
            "object": ValueType.OBJECT,
        }.get(normalized, ValueType.OBJECT)
    
    # Return implementation
    def _ret(self, frame: ExecutionFrame) -> None:
        """Return from method"""
        if frame.stack:
            frame.return_value = frame.pop()
    
    def get_output(self) -> str:
        """Get captured console output"""
        return '\n'.join(self.console_output)
    
    def  _execute_if(self, frame: ExecutionFrame, instruction: str) -> None:
        """Handle if control flow by checking condition on top of stack."""
        match = re.search(r'if\s*\(([^)]*)\)', instruction)
        if not match:
            return
    
        condition_expr = match.group(1)
        condition_value = frame.pop()
        
        # Currently, the executor only supports checking stack value for bool type and true equals 1
        if condition_value.type_ != ValueType.BOOL or (condition_value.data is not True):
            print("Value is not a bool")
            return
            
        target_block = self._parse_if_body(instruction)
        self._execute_block(frame, target_block)