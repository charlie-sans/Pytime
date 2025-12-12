# If Statements and Control Flow

### `if` - Conditional Statement

**Description**: Executes a block of code conditionally based on a condition.

**Syntax**:
```
if (<condition>) {
    <then-instructions>
}
```

or

```
if (<condition>) {
    <then-instructions>
} else {
    <else-instructions>
}
```

**Condition Types**:
- `stack`: Uses the boolean value on top of the stack
- Comparison expression: e.g., `a < b`

**Example**:
```
method Max(a: int32, b: int32) -> int32 {
    ldarg a
    ldarg b
    cgt
    
    if (stack) {
        ldarg a
        ret
    } else {
        ldarg b
        ret
    }
}
```

---

### `while` - Loop Statement

**Description**: Repeats a block of code while a condition is true.

**Syntax**:
```
while (<condition>) {
    <body-instructions>
}
```

**Example**:
```
method CountDown(n: int32) -> void {
    local i: int32
    ldarg n
    stloc i
    
    while (i > 0) {
        ldloc i
        call System.Console.WriteLine(int32) -> void
        
        ldloc i
        ldc.i4 1
        sub
        stloc i
    }
}
```

---

### `break` - Break from Loop

**Description**: Exits the current loop immediately.

**Syntax**:
```
break
```

**Example**:
```
while (true) {
    ldloc counter
    ldc.i4 10
    cge
    
    if (stack) {
        break    // Exit the loop
    }
    
    ldloc counter
    ldc.i4 1
    add
    stloc counter
}
```

---

### `continue` - Continue Loop

**Description**: Skips the rest of the current loop iteration and continues with the next iteration.

**Syntax**:
```
continue
```

**Example**:
```
while (i < 10) {
    ldloc i
    ldc.i4 2
    rem
    ldc.i4 0
    ceq
    
    if (stack) {
        ldloc i
        ldc.i4 1
        add
        stloc i
        continue    // Skip even numbers
    }
    
    ldloc i
    call Print(int32) -> void
    
    ldloc i
    ldc.i4 1
    add
    stloc i
}
```

---
### Example 1: Conditional Logic

```
module Comparison version 1.0.0

class Logic {
    method Max(a: int32, b: int32) -> int32 {
        ldarg a
        ldarg b
        cgt
        
        if (stack) {
            ldarg a
            ret
        } else {
            ldarg b
            ret
        }
    }
    
    method IsEven(n: int32) -> bool {
        ldarg n
        ldc.i4 2
        rem
        ldc.i4 0
        ceq
        ret
    }
}
```

### Example 2: Loop with Break and Continue

```
module LoopDemo version 1.0.0

class Loops {
    method PrintOddNumbers(max: int32) -> void {
        local i: int32
        ldc.i4 0
        stloc i
        
        while (i < max) {
            ldloc i
            ldc.i4 10
            cge
            
            if (stack) {
                break
            }
            
            ldloc i
            ldc.i4 2
            rem
            ldc.i4 0
            ceq
            
            if (stack) {
                ldloc i
                ldc.i4 1
                add
                stloc i
                continue
            }
            
            ldloc i
            call System.Console.WriteLine(int32) -> void
            
            ldloc i
            ldc.i4 1
            add
            stloc i
        }
    }
}
```
### Example 3: Factorial Function

```
module Factorial version 1.0.0

class Math {
    method Factorial(n: int32) -> int32 {
        local result: int32
        local i: int32
        
        ldc.i4 1
        stloc result
        
        ldc.i4 2
        stloc i
        
        while (i <= n) {
            ldloc result
            ldloc i
            mul
            stloc result
            
            ldloc i
            ldc.i4 1
            add
            stloc i
        }
        
        ldloc result
        ret
    }
}
```