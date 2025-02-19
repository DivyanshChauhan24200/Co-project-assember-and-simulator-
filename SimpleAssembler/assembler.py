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
