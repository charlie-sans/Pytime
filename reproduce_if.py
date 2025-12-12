
from oir_parser import ObjectIRParser
from oir_executor import InstructionExecutor
from oir_frame import ExecutionFrame

code = """
module Test {
    class Main {
        method Run() -> void {
            ldc.i4 1
            ldc.i4 2
            ceq
            if (stack) {
                ldstr "True branch executed (Should NOT happen)"
                call System.Console.WriteLine(string) -> void
            } else {
                ldstr "False branch executed (Should happen)"
                call System.Console.WriteLine(string) -> void
            }
            ldstr "Done"
            call System.Console.WriteLine(string) -> void
        }
    }
}
"""

parser = ObjectIRParser()
parser.parse(code)
instructions = parser.methods['Run']
print("Instructions:", instructions)

executor = InstructionExecutor()
frame = ExecutionFrame("Run")
# We need to manually execute instructions since there is no main loop in executor exposed yet for a list of instructions
# But wait, executor.execute_instruction takes a single instruction.
# So we need a loop here.

print("\nExecuting:")
executor.execute_method(frame, instructions)

print("\nOutput:")
print(executor.get_output())
