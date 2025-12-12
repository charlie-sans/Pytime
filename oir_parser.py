"""
ObjectIR text format parser
"""

import re
from typing import List, Dict, Any, Optional


class ObjectIRParser:
    """Parses ObjectIR text format files"""
    
    def __init__(self):
        self.modules: Dict[str, Dict[str, Any]] = {}
        self.current_module: str = None
        self.classes: Dict[str, Dict[str, Any]] = {}
        self.methods: Dict[str, List[str]] = {}  # method_name -> instructions
        self.current_method: str = None
    
    def parse_file(self, filepath: str) -> None:
        """Parse an ObjectIR text file"""
        with open(filepath, 'r') as f:
            content = f.read()
        self.parse(content)
    
    def parse(self, content: str) -> None:
        """Parse ObjectIR text format"""
        lines = content.strip().split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            i += 1
            
            # Skip empty lines and comments
            if not line or line.startswith('//'):
                continue
            
            # Module declaration
            if line.startswith('module '):
                self.current_module = line.replace('module ', '').strip()
                self.modules[self.current_module] = {'classes': {}}
                continue
            
            # Class declaration
            if line.startswith('class '):
                match = re.match(r'class\s+(\w+)\s*\{', line)
                if match:
                    class_name = match.group(1)
                    self.classes[class_name] = {'methods': {}}
                    if self.current_module:
                        self.modules[self.current_module]['classes'][class_name] = {'methods': {}}
                continue
            
            # Method declaration
            if line.startswith('method '):
                # method Name(args) -> ReturnType {
                match = re.match(r'method\s+(\w+)\s*\((.*?)\)\s*->\s*(\w+(?:\.\w+)*)\s*\{', line)
                if match:
                    method_name = match.group(1)
                    args_str = match.group(2)
                    return_type = match.group(3)
                    self.current_method = method_name
                    self.methods[method_name] = []
                    
                    # Collect method instructions until closing brace
                    i = self._parse_method_body(lines, i, method_name)
    
    def _parse_method_body(self, lines: List[str], start_idx: int, method_name: str) -> int:
        """Parse method body and collect instructions"""
        instructions = []
        brace_count = 1
        
        i = start_idx
        while i < len(lines):
            line = lines[i].strip()
            i += 1
            
            if not line or line.startswith('//'):
                continue
            
            # Count braces
            brace_count += line.count('{') - line.count('}')
            
            if brace_count == 0:
                self.methods[method_name] = instructions
                return i
            
            # Parse instruction
            if brace_count > 0 and line:
                # Handle if statements with complex conditions
                if line.startswith('if '):
                    # Parse the full if statement including condition and body
                    if_block, next_index = self._parse_if_statement(lines, i-1)
                    instructions.extend(if_block)
                    i = next_index
                else:
                    instructions.append(line)
        
        return len(lines)
    
    def _parse_if_statement(self, lines: List[str], start_idx: int) -> tuple[List[str], int]:
        """Parse if statement with condition and body"""
        if_block = []
        i = start_idx
        brace_count = 0
        
        while i < len(lines):
            line = lines[i].strip()
            i += 1
            
            if not line or line.startswith('//'):
                continue
            
            # Check if this is the start of the if statement
            if line.startswith('if '):
                if_block.append(line)
                # Check if the if statement has an opening brace on the same line
                if '{' in line:
                    brace_count = line.count('{') - line.count('}')
                continue
            # Count braces for nested blocks
            brace_count += line.count('{') - line.count('}')
            
            if_block.append(line)
            
            # If we've closed all braces, we're done with this if statement
            if brace_count == 0 and '}' in line:
                # Check if there's an else clause
                if i < len(lines) and lines[i].strip().startswith('else'):
                    else_line = lines[i].strip()
                    if_block.append(else_line)
                    i += 1
                    # Parse else body
                    if '{' in else_line:
                        else_brace_count = else_line.count('{') - else_line.count('}')
                        while i < len(lines) and else_brace_count > 0:
                            else_body_line = lines[i].strip()
                            i += 1
                            if not else_body_line or else_body_line.startswith('//'):
                                continue
                            if_block.append(else_body_line)
                            else_brace_count += else_body_line.count('{') - else_body_line.count('}')
                else: 
                    # No else clause, we are done
                    pass
                break
           

        return if_block, i
    
    def _find_matching_brace(self, text: str, start: int) -> Optional[int]:
        """Find matching brace from a given starting position."""
        level = 1
        for i in range(start + 1, len(text)):
            if text[i] == '{':
                level += 1
            elif text[i] == '}':
                level -= 1
            if level == 0:
                return i
        return None  # unbalanced braces
    
    def _parse_if_body(self, instruction: str) -> List[str]:
        """Parse if block and return the instructions within."""
        start = instruction.find('{') + 1
        end = self._find_matching_brace(instruction, start)

        # Extract body content inside braces
        if end is not None:
            body = instruction[start:end].strip()
            lines = [line.strip() for line in body.split('\n') if line.strip() and not line.strip().startswith("//")]
            return lines
        return []