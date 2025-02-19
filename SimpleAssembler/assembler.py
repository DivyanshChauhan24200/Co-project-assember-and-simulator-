import re
import sys
registers = {"zero": 0,"x0":0,"ra": 1,
    "sp": 2,
    "gp": 3,
    "tp": 4,
    "t0": 5,
    "t1": 6,
    "t2": 7,
    "s0": 8,
    "s1": 9,
    "a0": 10,
    "a1": 11,
    "a2": 12,
    "a3": 13,
    "a4": 14,
    "a5": 15,
    "a6": 16,
    "a7": 17,
    "s2": 18,
    "s3": 19,
    "s4": 20,
    "s5": 21,
    "s6": 22,
    "s7": 23,
    "s8": 24,
    "s9": 25,
    "s10": 26,
    "s11": 27,
    "t3": 28,
    "t4": 29,
    "t5": 30,
    "t6": 31
}
opcode = {
    "add": "0110011",
    "sub": "0110011",
    "slt": "0110011",
    "srl": "0110011",
    "or": "0110011",
    "and": "0110011",
    "lw": "0000011",
    "addi": "0010011",
    "jalr": "1100111",
    "sw": "0100011",
    "beq": "1100011",
    "bne": "1100011",
    "blt": "1100011",
    "jal": "1101111",

}
def RegToNum(reg):
    if reg in registers.keys():
        return registers[reg]
    else:
        return -1
def R_type(inst, rd, rs1, rs2):
    funct = {
        "add": {"funct3": "000", "funct7": "0000000"},
        "sub": {"funct3": "000", "funct7": "0100000"},
        "slt": {"funct3": "010", "funct7": "0000000"},
        "srl": {"funct3": "101", "funct7": "0000000"},
        "or":  {"funct3": "110", "funct7": "0000000"},
        "and": {"funct3": "111", "funct7": "0000000"}
    }
    return (funct[inst]["funct7"]+
            format(rs2, '05b') +
            format(rs1, '05b') +
            funct[inst]["funct3"]+
            format(rd, '05b') +
            opcode[inst])

def I_type(inst, rd, rs1, imidate):
    funct3 = {
        "lw": "010",
        "addi": "000",
        "jalr": "000"
    }
    return (format(imidate & 0xFFF, '012b') +
            format(rs1, '05b') +
            funct3[inst] +
            format(rd, '05b') +
            opcode[inst])
def B_type(inst, rs1, rs2, imm):
    funct3 = {
        "beq": "000",
        "bne": "001",
        "blt": "100",
    }
    immd = imm >> 1  
    b_imm = format(immd & 0xfff, '012b')
    return (b_imm[0] +            
            b_imm[2:8] +        
            format(rs2, '05b') +  
            format(rs1, '05b') +  
            funct3[inst]+  
            b_imm[8:12] +        
            b_imm[1] +            
            opcode[inst])
def J_type(inst, rd, imm):
    j_imm = format(imm & 0x1fffff, '021b')
    imm_20 = j_imm[0] + j_imm[10:20] + j_imm[9] + j_imm[1:9]
    return (imm_20 +
            format(rd, '05b') +
            opcode[inst])
def S_type(inst, rs2, rs1, imm):
    b_imm = format(imm & 0xfff, '012b')
    return (b_imm[0:7] +
            format(rs2, '05b') +
            format(rs1, '05b') +
            "010"+
            b_imm[7:12] +
            opcode[inst])

def code_parse(assembly_lines):
    labels = {}
    instructions = []
    current_address = 0
    for line in assembly_lines:
        line = line.strip()
        if not line:
            continue
        while ':' in line:
            label_part, remainder = line.split(":", 1)
            label = label_part.strip()
            if label:
                labels[label] = current_address
            line = remainder.strip()
        if line:
            instructions.append(line)
            current_address += 4
    return labels, instructions

def machine_code(instuctions, labels, lineNo):
    instruction_fields = re.split(r'[ ,]+', instuctions.strip())
    inst = instruction_fields[0]
    if inst not in opcode.keys():
        return f"Error: Invalid instruction {inst} at line {lineNo}"
    if inst == 'addi' and instruction_fields == 'addi x0, x0, 0':
        return '00000000000000000000000000000000' 
    if inst == 'halt':
        return '11111111111111111111111111111111'
    if inst in ("add", "sub", "slt","srl", "or", "and"):
        if len(instruction_fields)!=4:
            return f"Syntax Error at line {lineNo}"

        rd = RegToNum(instruction_fields[1])
        rs1 = RegToNum(instruction_fields[2])
        rs2 = RegToNum(instruction_fields[3])
        lis1=[rd,rs1,rs2]

        for i in lis1:
            if i==-1:
                return f"Error: Invalid register name at line {lineNo}"
        return R_type(inst, rd, rs1, rs2)
        
    elif inst in ("addi", "lw", "jalr"):
        if inst == 'jalr':
            if len(instruction_fields)!=4:
                return f"Syntax Error at line {lineNo}"
           
            rd = RegToNum(instruction_fields[1])
            rs1 = RegToNum(instruction_fields[2])
            Imi = int(instruction_fields[3])
            lis2=[rd,rs1]
            for i in lis2:
                if i==-1:
                    return f"Error: Invalid register name at line {lineNo}"

            return I_type(inst, rd, rs1, Imi)
        elif inst in ("lw"):
            if len(instruction_fields)!=3:
                return f"Syntax Error at line {lineNo}"
            rd = RegToNum(instruction_fields[1])
            offset_reg = instruction_fields[2]
            if '(' in offset_reg and ')' in offset_reg:
                offset_reg = offset_reg.strip(')')
                offset, reg = offset_reg.split('(')
                offset = int(offset)
                rs1 = RegToNum(reg.strip())
                lis3=[rd,rs1]
                for i in lis3:
                    if i==-1:
                        return f"Error: Invalid register name at line {lineNo}"
            else:
                return f"Error: Invalid memory operand in lw at line {lineNo}"

            return I_type(inst, rd, rs1, offset)
        else:
            if len(instruction_fields)!=4:
                return f"Syntax Error at line {lineNo}"
            rd = RegToNum(instruction_fields[1])
            rs1 = RegToNum(instruction_fields[2])
            Imi = int(instruction_fields[3])
            lis3=[rd,rs1]
            for i in lis3:
                if i==-1:
                    return f"Error: Invalid register name at line {lineNo}"
            return I_type(inst, rd, rs1, Imi)
    elif inst =="sw":
        if len(instruction_fields)!=3:
            return f"Syntax Error at line {lineNo}"
        rs2 = RegToNum(instruction_fields[1])
        offset_reg = instruction_fields[2]
        if '(' in offset_reg and ')' in offset_reg:
            offset_reg = offset_reg.strip(')')
            Imi, reg = offset_reg.split('(')
            Imi = int(Imi)
            rs1 = RegToNum(reg.strip())
            lis4=[rs1,rs2]
            for i in lis4:
                if i==-1:
                    return f"Error: Invalid register name at line {lineNo}"
        else:
            return f"Error: Invalid memory operand at line {lineNo}"
    
        return S_type(inst, rs2, rs1, Imi)
