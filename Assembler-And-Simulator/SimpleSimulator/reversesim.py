opcodes = { 
    'add' : '0110011', 'sub' : '0110011', 'sll' : '0110011', 'slt' : '0110011', 'sltu' : '0110011', 'xor' : '0110011', 'srl' : '0110011', 'or' : '0110011', 'and' : '0110011',
    'lw' : '0000011', 'addi' : '0010011', 'sltiu' : '0010011', 'jalr' : '1100111',
    'sw' : '0100011',
    'beq' : '1100011', 'bne' : '1100011', 'blt' : '1100011', 'bge' : '1100011', 'bltu' : '1100011', 'bgeu' : '1100011',
    'lui' : '0110111', 'auipc' : '0010111',
    'jal' : '1101111',
}

# for different types of commands in the processor/assembler
types = {
    'R' : ['add','sub','sll','slt','sltu','xor','srl','or','and'],
    'I' : ['lw','addi','sltiu','jalr'],
    'S' : ['sw'],
    'B' : ['beq','bne','blt','bge','bltu','bgeu'],
    'U' : ['lui', 'auipc'],
    'J' : ['jal'],
}

registers = {
    "zero": "00000", "ra": "00001", "sp": "00010", "gp": "00011", "tp": "00100",
    "t0": "00101", "t1": "00110", "t2": "00111", "s0": "01000", "s1": "01001",
    "a0": "01010", "a1": "01011", "a2": "01100", "a3": "01101", "a4": "01110",
    "a5": "01111", "a6": "10000", "a7": "10001", "s2": "10010", "s3": "10011",
    "s4": "10100", "s5": "10101", "s6": "10110", "s7": "10111", "s8": "11000",
    "s9": "11001", "s10": "11010", "s11": "11011", "t3": "11100", "t4": "11101",
    "t5": "11110", "t6": "11111"
}

reg_mem = {}

rev_regs = {v: k for k, v in registers.items()}

VIRTUAL_HALT_INSTRUCTION_BIN = "00000000000000000000000001100011"

def reverse_assembler(binary_string):
    # Reverse the opcodes dictionary to get the instruction names
    opcodes_reverse = {v: k for k, v in opcodes.items()}
    
    # Split the binary string into 32-bit chunks
    chunks = [binary_string[i:i+32] for i in range(0, len(binary_string), 32)]
    
    # Initialize an empty list to store the instructions
    instructions = []
    
    # Iterate over the chunks and convert them back to instructions
    for chunk in chunks:
        opcode = chunk[-7:]
        
        # Check if the opcode is a virtual halt instruction
        if opcode == VIRTUAL_HALT_INSTRUCTION_BIN:
            instructions.append("virtual_halt")
            continue
        
        # Get the instruction name based on the opcode
        instruction = opcodes_reverse.get(opcode)
        
        # Check if the instruction is of type R
        if instruction in types['R']:
            funct3 = chunk[-15:-12]
            funct7 = chunk[-32:-25]
            rd = bin_to_abi(chunk[-12:-7])
            rs1 = bin_to_abi(chunk[-20:-15])
            rs2 = bin_to_abi(chunk[-25:-20])
            instructions.append(f"{instruction} {rd}, {rs1}, {rs2}")
        
        # Check if the instruction is of type I
        elif instruction in types['I']:
            funct3 = chunk[-15:-12]
            rd = bin_to_abi(chunk[-12:-7])
            rs = bin_to_abi(chunk[-20:-15])
            imm = bin_to_dec(chunk[:-20])
            instructions.append(f"{instruction} {rd}, {rs}, {imm}")
        
        # Check if the instruction is of type S
        elif instruction in types['S']:
            funct3 = chunk[-15:-12]
            rs2 = bin_to_abi(chunk[-25:-20])
            rs1 = bin_to_abi(chunk[-20:-15])
            imm = bin_to_dec(chunk[:-25] + chunk[-12:-7])
            instructions.append(f"{instruction} {rs2}, {imm}({rs1})")
        
        # Check if the instruction is of type B
        elif instruction in types['B']:
            funct3 = chunk[-15:-12]
            rs1 = bin_to_abi(chunk[-20:-15])
            rs2 = bin_to_abi(chunk[-25:-20])
            imm = bin_to_dec(chunk[0] + chunk[24] + chunk[1:7] + chunk[20:24] + "0")
            instructions.append(f"{instruction} {rs1}, {rs2}, {imm}")
        
        # Check if the instruction is of type U
        elif instruction in types['U']:
            rd = bin_to_abi(chunk[-12:-7])
            imm = bin_to_dec(chunk[:-12] + chunk[-32:-12])
            instructions.append(f"{instruction} {rd}, {imm}")
        
        # Check if the instruction is of type J
        elif instruction in types['J']:
            rd = bin_to_abi(chunk[-12:-7])
            imm = bin_to_dec(chunk[0] + chunk[12:20] + chunk[11] + chunk[1:11] + "0")
            instructions.append(f"{instruction} {rd}, {imm}")
    
    return instructions


def to_dec(binary, unsigned=False):
    if '0b' in binary:
        binary = binary[2:]
    if not unsigned and binary[0] == "1":
        inverted_binary = "".join(["1" if bit == "0" else "0" for bit in binary])
        decimal_number = int(inverted_binary, 2) + 1
        return -decimal_number
    else:
        return int(binary, 2)

def bin_to_abi(binary, unsigend=False):
    # Convert the binary string to ABI register name
    # Implement the reverse logic of bin_from_abi function
    
    for register, value in registers.items():
        if value == binary:
            return register + '(x' + str(int(binary, 2)) + ': ' + str(to_dec(reg_mem[binary], unsigend)) + ')'
    return None

def bin_to_dec(binary):
    # Convert the binary string to decimal number
    # Implement the reverse logic of to_dec function
    decimal = int(binary, 2)
    if binary[0] == '1':
        decimal -= 2 ** len(binary)
    return decimal

if __name__ == "__main__":
    infile = 's_test3_input.txt'

    # Example usage
    with open(infile) as f:
        lines = f.readlines()

    i_memory = {}
    i = 0
    for line in lines:
        binary_string = line.strip()
        instructions = reverse_assembler(binary_string)
        i_memory[i*4] = instructions
        # print(format(i*4, '02d'), ': ', instructions[0])
        print(instructions[0])
        i += 1

    # with open('Simulator/s_test2.txt') as f:
    #     lines = f.readlines()

    #     for line in lines:
    #         pc = line.strip().split()[0]
    #         if pc[:2] == '0b':
    #             pc = int(pc, 2)
    #             print(i_memory[pc-4])