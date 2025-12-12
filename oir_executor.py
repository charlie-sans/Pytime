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
        elif opcode == 'ldarg':
            self._ldarg(frame, parts)
        elif opcode == 'ldcon':
            self._ldcon(frame, parts)
        elif opcode == 'ldtrue':
            self._ldc_bool(frame, True)
        elif opcode == 'ldfalse':
            self._ldc_bool(frame, False)
        
        # Store instructions
        elif opcode == 'stloc':
            self._stloc(frame, parts)
        elif opcode == 'starg':
            self._starg(frame, parts)
        
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
        elif opcode == 'neg':
            self._neg(frame)
        
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
        elif opcode == 'cne':
            self._cne(frame)
        
        # Stack manipulation
        elif opcode == 'dup':
            self._dup(frame)
        elif opcode == 'pop':
            self._pop(frame)
        elif opcode == 'nop':
            pass
        elif opcode == 'throw':
            self._throw(frame)
        elif opcode == 'local':
            # Initialize local variable with default value
            self._local(frame, parts)

        elif opcode == 'if':
            pass  # Control flow instructions are handled at a higher level
        
        # Built-in method calls
        elif opcode == 'call' or opcode == 'callvirt':
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
    
    def _ldarg(self, frame: ExecutionFrame, parts: list) -> None:
        """Load argument"""
        arg_name = parts[1]
        value = frame.get_arg(arg_name)
        frame.push(value)

    def _ldcon(self, frame: ExecutionFrame, parts: list) -> None:
        """Load generic constant"""
        value_str = ' '.join(parts[1:])
        # Simple inference
        if value_str.startswith('"') and value_str.endswith('"'):
            value = Value(value_str[1:-1], ValueType.STRING)
        elif value_str.lower() == 'true':
            value = Value(True, ValueType.BOOL)
        elif value_str.lower() == 'false':
            value = Value(False, ValueType.BOOL)
        elif '.' in value_str:
            value = Value(float(value_str), ValueType.DOUBLE)
        else:
            try:
                value = Value(int(value_str), ValueType.INT32)
            except ValueError:
                value = Value(value_str, ValueType.STRING) # Fallback
        frame.push(value)
    
    def _starg(self, frame: ExecutionFrame, parts: list) -> None:
        """Store to argument"""
        arg_name = parts[1]
        value = frame.pop()
        frame.set_arg(arg_name, value)
    
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
    
    def _neg(self, frame: ExecutionFrame) -> None:
        """Negate value"""
        val = frame.pop()
        result = -val.data
        frame.push(Value(result, val.type_))
    
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

    def _cne(self, frame: ExecutionFrame) -> None:
        """Compare not equal"""
        b = frame.pop()
        a = frame.pop()
        result = a.data != b.data
        frame.push(Value(result, ValueType.BOOL))
    
    # Stack manipulation implementations
    def _dup(self, frame: ExecutionFrame) -> None:
        """Duplicate top of stack"""
        value = frame.peek()
        frame.push(value)
    
    def _pop(self, frame: ExecutionFrame) -> None:
        """Pop value from stack"""
        frame.pop()

    def _throw(self, frame: ExecutionFrame) -> None:
        """Throw exception"""
        ex = frame.pop()
        raise RuntimeError(f"VM Exception: {ex.data}")

    def _local(self, frame: ExecutionFrame, parts: list) -> None:
        """Declare local variable: local name: type"""
        # parts: ['local', 'name:', 'type'] or ['local', 'name', ':', 'type']
        # The parser splits by space.
        # Example: local i: int32 -> ['local', 'i:', 'int32']
        # Example: local result: int32 -> ['local', 'result:', 'int32']
        
        # Join parts to parse manually
        line = ' '.join(parts[1:])
        if ':' in line:
            name, type_name = line.split(':', 1)
            name = name.strip()
            type_name = type_name.strip()
            
            # Initialize with default value
            val_type = self._resolve_value_type(type_name)
            default_val = None
            if val_type == ValueType.INT32 or val_type == ValueType.INT64:
                default_val = 0
            elif val_type == ValueType.FLOAT or val_type == ValueType.DOUBLE:
                default_val = 0.0
            elif val_type == ValueType.BOOL:
                default_val = False
            
            frame.set_local(name, Value(default_val, val_type))
    
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

    def execute_method(self, frame: ExecutionFrame, instructions: List[str]) -> None:
        """Execute a list of instructions"""
        frame.pc = 0
        loop_stack = [] # Stack of (start_pc, end_pc) for loops
        
        while frame.pc < len(instructions):
            instruction = instructions[frame.pc]
            current_pc = frame.pc
            frame.pc += 1
            
            parts = instruction.strip().split()
            if not parts:
                continue
            
            opcode = parts[0]
            
            # Handle comments
            if instruction.strip().startswith('//'):
                continue

            if opcode.startswith('if'):
                self._handle_if(frame, instructions, current_pc)
            elif opcode.startswith('while'):
                self._handle_while(frame, instructions, current_pc, loop_stack)
            elif opcode == 'break':
                if not loop_stack:
                    print("Warning: break outside of loop")
                    continue
                _, end_pc = loop_stack[-1]
                frame.pc = end_pc + 1
            elif opcode == 'continue':
                if not loop_stack:
                    print("Warning: continue outside of loop")
                    continue
                start_pc, _ = loop_stack[-1]
                frame.pc = start_pc
            elif opcode == 'else' or instruction.strip().startswith('} else'):
                # If we hit else/else block naturally, we finished the if block, so skip else
                self._skip_block(frame, instructions, current_pc)
            elif opcode == '}':
                self._handle_close_brace(frame, instructions, current_pc, loop_stack)
            else:
                self.execute_instruction(frame, instruction)
            
            if frame.return_value is not None:
                break

    def _scan_matching_brace(self, instructions: List[str], start_index: int) -> int:
        """Find the index of the matching closing brace"""
        balance = 0
        for i in range(start_index, len(instructions)):
            line = instructions[i].strip()
            # Handle comments in scan?
            if '//' in line:
                line = line.split('//')[0]
            
            for char in line:
                if char == '{':
                    balance += 1
                elif char == '}':
                    balance -= 1
                    if balance == 0:
                        return i
        return len(instructions)

    def _handle_if(self, frame: ExecutionFrame, instructions: List[str], current_pc: int) -> None:
        instruction = instructions[current_pc]
        # Parse condition
        match = re.search(r'if\s*\(([^)]*)\)', instruction)
        condition_true = False
        if match:
            cond = match.group(1).strip()
            if cond == 'stack':
                val = frame.pop()
                condition_true = (val.type_ == ValueType.BOOL and val.data)
            else:
                condition_true = self._evaluate_condition(frame, cond)

        if not condition_true:
            # Skip the if block
            end_index = self._scan_matching_brace(instructions, current_pc)
            
            # Check if there is an else block attached to the closing brace or next line
            end_line = instructions[end_index].strip()
            if 'else' in end_line:
                # We are at `} else {`. We should enter the else block.
                frame.pc = end_index + 1
            else:
                # Just `}`, so we are done.
                frame.pc = end_index + 1
                # Check if next line is `else` (if parser split it)
                if frame.pc < len(instructions) and instructions[frame.pc].strip().startswith('else'):
                    frame.pc += 1 # Enter else block

    def _handle_while(self, frame: ExecutionFrame, instructions: List[str], current_pc: int, loop_stack: List) -> None:
        instruction = instructions[current_pc]
        match = re.search(r'while\s*\(([^)]*)\)', instruction)
        condition_true = False
        if match:
             cond = match.group(1).strip()
             condition_true = self._evaluate_condition(frame, cond)
        
        if condition_true:
            end_index = self._scan_matching_brace(instructions, current_pc)
            loop_stack.append((current_pc, end_index))
            # print(f"DEBUG: while pushed {current_pc}, {end_index}")
        else:
            end_index = self._scan_matching_brace(instructions, current_pc)
            frame.pc = end_index + 1

    def _evaluate_condition(self, frame: ExecutionFrame, cond: str) -> bool:
        # Simple evaluator for "a < b", "stack", "true"
        if cond == 'stack':
            val = frame.pop()
            return val.data is True
        if cond == 'true': return True
        if cond == 'false': return False
        
        # Binary ops
        for op in ['<=', '>=', '==', '!=', '<', '>']:
            if op in cond:
                parts = cond.split(op)
                if len(parts) == 2:
                    left, right = parts
                    lval = self._eval_operand(frame, left.strip())
                    rval = self._eval_operand(frame, right.strip())
                    if op == '<': return lval < rval
                    if op == '>': return lval > rval
                    if op == '<=': return lval <= rval
                    if op == '>=': return lval >= rval
                    if op == '==': return lval == rval
                    if op == '!=': return lval != rval
        
        return False

    def _eval_operand(self, frame: ExecutionFrame, op: str):
        # Try integer
        try: return int(op)
        except: pass
        # Try local
        try: return frame.get_local(op).data
        except: pass
        # Try arg
        try: return frame.get_arg(op).data
        except: pass
        return 0

    def _handle_close_brace(self, frame: ExecutionFrame, instructions: List[str], current_pc: int, loop_stack: List) -> None:
        # Check if this brace matches the current loop end
        if loop_stack:
            start_pc, end_pc = loop_stack[-1]
            if current_pc == end_pc:
                # We reached the end of the loop. Jump back to start.
                frame.pc = start_pc
                loop_stack.pop()
                return

    def _skip_block(self, frame: ExecutionFrame, instructions: List[str], current_pc: int) -> None:
         end_index = self._scan_matching_brace(instructions, current_pc)
         frame.pc = end_index + 1