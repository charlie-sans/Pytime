
from oir_parser import ObjectIRParser
from oir_executor import InstructionExecutor
from oir_frame import ExecutionFrame

def test_if():
    print("\n--- Testing IF ---")
    code = """
    module Test {
        class Main {
            method Run() -> void {
                ldc.i4 1
                ldc.i4 2
                ceq
                if (stack) {
                    ldstr "FAIL: 1 == 2"
                    call System.Console.WriteLine(string) -> void
                } else {
                    ldstr "PASS: 1 != 2"
                    call System.Console.WriteLine(string) -> void
                }
                
                ldc.i4 1
                ldc.i4 1
                ceq
                if (stack) {
                    ldstr "PASS: 1 == 1"
                    call System.Console.WriteLine(string) -> void
                }
            }
        }
    }
    """
    run_test(code)

def test_while():
    print("\n--- Testing WHILE ---")
    code = """
    module Test {
        class Main {
            method Run() -> void {
                local i: int32
                ldc.i4 0
                stloc i
                
                while (i < 3) {
                    ldloc i
                    call System.Console.WriteLine(int32) -> void
                    
                    ldloc i
                    ldc.i4 1
                    add
                    stloc i
                }
                ldstr "Done"
                call System.Console.WriteLine(string) -> void
            }
        }
    }
    """
    run_test(code)

def test_break_continue():
    print("\n--- Testing BREAK/CONTINUE ---")
    code = """
    module Test {
        class Main {
            method Run() -> void {
                local i: int32
                ldc.i4 0
                stloc i
                
                while (i < 5) {
                    ldloc i
                    ldc.i4 1
                    add
                    stloc i
                    
                    ldloc i
                    ldc.i4 2
                    ceq
                    if (stack) {
                        ldstr "Skipping 2"
                        call System.Console.WriteLine(string) -> void
                        continue
                    }
                    
                    ldloc i
                    ldc.i4 4
                    ceq
                    if (stack) {
                        ldstr "Breaking at 4"
                        call System.Console.WriteLine(string) -> void
                        break
                    }
                    
                    ldloc i
                    call System.Console.WriteLine(int32) -> void
                }
            }
        }
    }
    """
    run_test(code)

def test_instructions():
    print("\n--- Testing Instructions ---")
    code = """
    module Test {
        class Main {
            method Run(arg1: int32) -> void {
                ldarg arg1
                call System.Console.WriteLine(int32) -> void
                
                ldc.i4 5
                neg
                call System.Console.WriteLine(int32) -> void
                
                ldc.i4 10
                ldc.i4 20
                cne
                if (stack) {
                    ldstr "PASS: 10 != 20"
                    call System.Console.WriteLine(string) -> void
                }
                
                nop
            }
        }
    }
    """
    run_test(code, {"arg1": 42})

def run_test(code, args=None):
    parser = ObjectIRParser()
    parser.parse(code)
    instructions = parser.methods['Run']
    print(f"Instructions: {instructions}")
    
    executor = InstructionExecutor()
    frame = ExecutionFrame("Run")
    if args:
        from oir_types import Value, ValueType
        for k, v in args.items():
            frame.set_arg(k, Value(v, ValueType.INT32))
            
    executor.execute_method(frame, instructions)
    print(executor.get_output())

if __name__ == "__main__":
    test_if()
    test_while()
    test_break_continue()
    test_instructions()
