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
    def trace_decimal(self, pc, registers):
        values = [str(pc)] + [str(r) for r in registers]
        return " ".join(values)
    def type_R(self,current_inst):
        funct7 = current_inst[0:7]
        rs2 = int(current_inst[7:12], 2)
        rs1 = int(current_inst[12:17], 2)
        funct3 = current_inst[17:20]
        rd = int(current_inst[20:25], 2)
        r1 = self.registers[rs1]
        r2 = self.registers[rs2]
        functs=[funct3,funct7]
        
        funct_map = {
            "ADD": ["000", "0000000"],  
            "SUB": ["000", "0100000"],  
            "OR": ["110", "0000000"],  
            "AND": ["111", "0000000"],  
            "SRL": ["101", "0000000"],  
            "SLT": ["010", "0000000"],  
        }

        if functs not in funct_map.values():
            print(f"Invalid R type instruction funct3={functs[0]} , funct7={functs[1]}")
        else:
            
            if funct_map["ADD"]==functs:
                result=self.ADD(r1,r2)
            elif funct_map["SUB"]==functs:
                result=self.SUB(r1,r2)
            elif funct_map["OR"]==functs:
                result=self.OR(r1,r2)
            elif funct_map["SRL"]==functs:
                result=self.SRL(r1,r2)
            elif funct_map["SLT"]==functs:
                result=self.SLT(r1,r2)
            elif funct_map["AND"]==functs:
                result=self.AND(r1,r2)
        self.write_register(rd, result)
        return self.pc+4
    def type_I_addi(self,current_inst):
        imm_field = current_inst[0:12]
        imm = int(imm_field, 2)
        imm = self.sign_extend(imm, 12)
        rs1 = int(current_inst[12:17], 2)
        funct3 = current_inst[17:20]
        rd = int(current_inst[20:25], 2)
        if funct3 == "000":
             result = self.registers[rs1] + imm
        else:
            print(f"invalid I-type funct3: {funct3}")
            sys.exit(1)
        self.write_register(rd, result)
        return self.pc+4
    def type_I_lw(self,current_inst):
        imm = int(current_inst[0:12], 2)
        imm = self.sign_extend(imm, 12)
        rs1 = int(current_inst[12:17], 2)
        funct3 = current_inst[17:20]
        rd = int(current_inst[20:25], 2)
        if funct3 == "010":
            addr = self.registers[rs1] + imm
           
            value = self.read_memory(addr)
            self.write_register(rd, value)
        else:
            print(f"invalid lw funct3: {funct3}")
            sys.exit(1)
        
        return self.pc+4
    def type_I_jalr(self,current_inst):
        imm = int(current_inst[0:12], 2)
        imm = self.sign_extend(imm, 12)
        rs1 = int(current_inst[12:17], 2)
        rd = int(current_inst[20:25], 2)
        target = (self.registers[rs1] + imm) & 0xFFFFFFFE
        self.write_register(rd, self.pc + 4)
        new_pc = target
        return new_pc
    def type_B(self,current_inst):
        imm_12 = current_inst[0]
        imm_10_5 = current_inst[1:7]
        imm_4_1 = current_inst[20:24]
        imm_11 = current_inst[24]
        imm = int(imm_12 + imm_11 + imm_10_5 + imm_4_1, 2)
        imm = self.sign_extend(imm, 12) << 1
        rs1 = int(current_inst[12:17], 2)
        rs2 = int(current_inst[7:12], 2)
        funct3 = current_inst[17:20]
        bt = False
        if funct3 == "000":
            if (self.registers[rs1] == self.registers[rs2]):
                bt=True
        elif funct3 == "001":
            if (self.registers[rs1] != self.registers[rs2]):
                bt=True
        else:
            print(f"Unsupported B-type funct3: {funct3}")
            sys.exit(1)
        if bt:
            return self.pc+imm
        else:
            return self.pc+4

    def type_J(self,current_inst):
        imm_20 = current_inst[0]
        imm_10_1 = current_inst[1:11]
        imm_11 = current_inst[11]
        imm_19_12 = current_inst[12:20]
        imm = int(imm_20 + imm_19_12 + imm_11 + imm_10_1, 2)
        imm = self.sign_extend(imm, 20) << 1
        rd = int(current_inst[20:25], 2)
        self.write_register(rd, self.pc + 4)
        new_pc = self.pc + imm
        return new_pc
    def type_S(self,current_inst):
        imm_high = current_inst[0:7]
        imm_low = current_inst[20:25]
        imm = int(imm_high + imm_low, 2)
        imm = self.sign_extend(imm, 12)
        rs1 = int(current_inst[12:17], 2)
        rs2 = int(current_inst[7:12], 2)
        funct3 = current_inst[17:20]
        if funct3 == "010":
            addr = self.registers[rs1] + imm
            # Use write_memory method
            self.write_memory(addr, self.registers[rs2])
        else:
            print(f"Unsupported sw funct3: {funct3}")
            sys.exit(1)
        return self.pc+4
    def run(self):
        while True:
            inst_index = self.pc // 4
            if inst_index < 0 or inst_index >= len(self.instructions):
                break

            current_inst = self.instructions[inst_index]
            
            if current_inst == "00000000000000000000000001100011":
                self.binary_trace.append(self.trace_binary(self.pc, self.registers))
                self.decimal_trace.append(self.trace_decimal(self.pc, self.registers))
                break
            if current_inst == "11111111111111111111111111111111":
                break

            new_pc = self.pc + 4
            opcode = current_inst[25:32]
            if opcode not in self.opcode_map.values():
                print(f"Invalid Opcode {opcode}")
                sys.exit(1)
            else:
                if self.opcode_map["R"]==opcode:
                    new_pc=self.type_R(current_inst)
                elif self.opcode_map["S"]==opcode:
                    new_pc=self.type_S(current_inst)
                elif self.opcode_map["lw"]==opcode:
                    new_pc=self.type_I_lw(current_inst)
                elif self.opcode_map["jalr"]==opcode:
                    new_pc=self.type_I_jalr(current_inst)
                elif self.opcode_map["addi"]==opcode:
                    new_pc=self.type_I_addi(current_inst)
                elif self.opcode_map["B"]==opcode:
                    new_pc=self.type_B(current_inst)
                elif self.opcode_map["J"]==opcode:
                    new_pc=self.type_J(current_inst)
                    

            self.pc = new_pc
            self.binary_trace.append(self.trace_binary(self.pc, self.registers))
            self.decimal_trace.append(self.trace_decimal(self.pc, self.registers))
        

        return self.binary_trace, self.decimal_trace, self.data_memory
def main():
    args = sys.argv[1:] 

    if len(args) < 2:
        sys.exit(1)

    input_file = args[0]
    output_base = args[1]

 
    if "." in output_base:
        file1 = output_base
        file2 = output_base.rsplit(".", 1)[0] + "_r." + output_base.rsplit(".", 1)[1]
    else:
        file1 = output_base + ".txt"
        file2 = output_base + "_r.txt"


    simulator = Simulator(input_file)
    bin_trace, dec_trace, data_mem = simulator.run()

 
    with open(file1, 'w') as f:
        for line in bin_trace:
            f.write(line + "\n")
        for i in range(len(data_mem)):
            addr = 0x00010000 + i * 4
            f.write(f"0x{addr:08X}:0b{data_mem[i]:032b}\n")


    with open(file2, 'w') as f:
        for line in dec_trace:
            f.write(line + "\n")
        for i in range(len(data_mem)):
            addr = 0x00010000 + i * 4
            f.write(f"0x{addr:08X}:{data_mem[i]}\n")


main()
