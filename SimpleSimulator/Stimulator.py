import sys

class Simulator:
    def __init__(self, input_file):
        self.instructions = self.load_instructions(input_file)
        self.registers = [0 for _ in range(32)]  
        self.registers[2] = 380    
        self.pc = 0         
        self.stack_memory = {}       
        self.data_memory =  {key: 0 for key in range(32)} 
        self.binary_trace = []
        self.opcode_map = {
            "R": "0110011",
            "addi": "0010011",
            "lw": "0000011",
            "S": "0100011",
            "B": "1100011",
            "J": "1101111",
            "jalr": "1100111"
        }

        self.decimal_trace = []
