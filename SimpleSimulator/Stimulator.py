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
    def write_memory(self, addr, value):
        
        if addr >= 65536 and addr < 65664:  
            mem_index = (addr - 65536) // 4
            if 0 <= mem_index < 32:  
                self.data_memory[mem_index] = value
        else:
            
            self.stack_memory[addr] = value

    def read_memory(self, addr):
        
        if addr >= 65536 and addr < 65664: 
            mem_index = (addr - 65536) // 4
            if 0 <= mem_index < 32:  
                return self.data_memory[mem_index]
            return 0
        else:
            
            return self.stack_memory.get(addr, 0)
    def load_instructions(self, input_file):
        instructions = []
        
        with open(input_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if len(line) != 32:
                    print(f"Invalid encoding at {line_num}")
                    sys.exit(1)
                
                instructions.append(line)

        return instructions
    @staticmethod
    def sign_extend(value, bits):
        threshold = 1 << (bits - 1)
        if value >= threshold:
            return value - (1 << bits)
        else:
            return value


    def write_register(self, rd, value):
        
        if rd >0:
            self.registers[rd] = value & 0xFFFFFFFF
    def trace_binary(self, pc, registers):
        
        pc_str = "0b" + bin(pc & 0xFFFFFFFF)[2:].zfill(32)

        
        regs_str = []
        for r in registers:
            bin_value = bin(r & 0xFFFFFFFF)[2:].zfill(32)
            regs_str.append("0b" + bin_value)

        
        return pc_str + " " + " ".join(regs_str)
            def ADD(self,r1,r2):
        result=r1+r2
        return result
    def SUB(self,r1,r2):
        result=r1-r2
        return result
    def OR(self,r1,r2):
        result=r1|r2
        return result
    def AND(self,r1,r2):
        result=r1&r2
        return result
    def SRL(self,r1,r2):
        shift = r2& 0x1F 
        result = r1>> shift
        return result
    def SLT(self,r1,r2):
        if r1<r2:
            return 1
        else:
            return 0
