# for different types of commands in the processor/assembler
types = {
    'R' : ['add','sub','sll','slt','sltu','xor','srl','or','and', 'mul'],
    'I' : ['lw','addi','sltiu','jalr'],
    'S' : ['sw'],
    'B' : ['beq','bne','blt','bge','bltu','bgeu'],
    'U' : ['lui', 'auipc'],
    'J' : ['jal'],
}
# for determining the variation in the same instruction in function field that helps in decoding the assembly code 
funct3s = {
    'add' : '000', 'sub' : '000', 'sll' : '001', 'slt' : '010', 'sltu' : '011', 'xor' : '100', 'srl' : '101', 'or' : '110', 'and' : '111', 'mul' : '111',
    'lw' : '010', 'addi' : '000', 'sltiu' : '011', 'jalr' : '000', 
    'sw' : '010',
    'beq' : '000', 'bne' : '001', 'blt' : '100', 'bge' : '101', 'bltu' : '110', 'bgeu' : '111',
}

# for determining the general type of instruction in command that occupies the most significant bit, allowing
# to read or decode the instruction type in which we get to know which function is used with the corresponding value in instruction code. 
opcodes = { 
    'add' : '0110011', 'sub' : '0110011', 'sll' : '0110011', 'slt' : '0110011', 'sltu' : '0110011', 'xor' : '0110011', 'srl' : '0110011', 'or' : '0110011', 'and' : '0110011', 'mul' : '0110011',
    'lw' : '0000011', 'addi' : '0010011', 'sltiu' : '0010011', 'jalr' : '1100111',
    'sw' : '0100011',
    'beq' : '1100011', 'bne' : '1100011', 'blt' : '1100011', 'bge' : '1100011', 'bltu' : '1100011', 'bgeu' : '1100011',
    'lui' : '0110111', 'auipc' : '0010111',
    'jal' : '1101111',
}

VIRTUAL_HALT_INSTRUCTION_BIN = "00000000000000000000000001100011"
error_Msg = ""

# below function tends to signify the signed  2s complement approach 
# to return the integer decimal form of the given binary string in the 2s complement notation system.
def to_dec(binary):
    if binary[0] == "1":
        inverted_binary = "".join(["1" if bit == "0" else "0" for bit in binary])
        decimal_number = int(inverted_binary, 2) + 1
        return -decimal_number
    else:
        return int(binary, 2)

def to_bin(n, bits, checkRange=True):
    bstr = None
    try:
        n = int(n)
        bstr = bin(n & int("1"*bits, 2))[2:]
    except:
        bstr = bin_from_abi(n)
    #n = int(n)
    #bstr = bin(n & int("1"*bits, 2))[2:]
    padded = bstr.zfill(bits)
    if checkRange and to_dec(padded) != n:
        global error_Msg
        error_Msg = "Incorrect Immediate"
        return None
    return str(padded)

# below bin_from_abi is responsible for converting ABI (Application Binary Interface) register names 
# to their corresponding binary representation to indicate the system.
def bin_from_abi(s):
    if s == 'zero':
        return '00000'
    if s == 'ra':
        return '00001'
    if s == 'sp':
        return '00010'
    if s == 'gp':
        return '00011'
    if s == 'tp':
        return '00100'
    if s == 't0':
        return '00101'
    if s == 't1' or s == 't2':
        return '00' + to_bin(int(s[1:]) + 5, 3, False)
    if s == 's0' or s == 'fp':
        return '01000'
    if s == 's1':
        return '01001'
    if s == 'a0' or s == 'a1':
        return '0101' + to_bin(int(s[1:]), 1, False)
    if s[0] == 'a':
        if 2 <= int(s[1:]) <= 5:
            return '011' + to_bin(int(s[1:]) - 2, 2, False)
        if 6 <= int(s[1:]) <= 7:
            return '1000' + to_bin((int(s[1:]) - 6), 1, False)
    if s[0] == 's' and 2 <= int(s[1:]) <= 11:
        return '1' + to_bin(int(s[1:]), 4, False) 
    if s[0] == 't' and 3 <= int(s[1:]) <= 6:
        return '111' + to_bin(int(s[1:]) - 3, 2, False)

    global error_Msg
    error_Msg = f"Invalid Register '{s}'"
    return None

# The below function is for parsing across the r-type instructions, including the identification of source registers and
#  returning the field function value and the instruction command value 
def parse_r_type(tokens):
    try:
        instruction, rd, rs1, rs2 = tokens
        funct7 = '0100000' if instruction == 'sub'or instruction == 'mul' else '0000000'
        return funct7 + bin_from_abi(rs2) + bin_from_abi(rs1) + funct3s[instruction] + bin_from_abi(rd) + opcodes[instruction]
    except:
# for exceptions or errors in notation while parsing raises an error if the instruction format is invalid as per our ISA.
        global error_Msg
        if error_Msg == "": error_Msg = "Invalid Instruction Format"
        return None


# The below function is for parsing across the i-type (immediate instructions, including the identification of source registers and
#  returning the field function value and the instruction command value .
def parse_i_type(tokens):
    try:
        instruction, rd, rs, imm = tokens
        if instruction == 'lw': rs,imm = imm,rs
        return to_bin(imm, 12) + bin_from_abi(rs) + funct3s[instruction] + bin_from_abi(rd) + opcodes[instruction]
    except:
# for exceptions or errors in notation while parsing raises an error if the instruction format is invalid as per our ISA.
        global error_Msg
        if error_Msg == "": error_Msg = "Invalid Instruction Format"
        return None

def parse_s_type(tokens):
    try:
        # Extract the tokens from the input
        instruction, rs2, imm, rs1 = tokens
        # Convert the immediate value to a binary string with a width of 12 bits
        bin_imm = to_bin(imm, 12)
        # Concatenate the binary representation parts according to RISC-V S-type format:
        # [immediate[11:5] | rs2 | rs1 | funct3 | immediate[4:0] | opcode]
        return bin_imm[0:7] + bin_from_abi(rs2) + bin_from_abi(rs1) + funct3s[instruction] + bin_imm[7:] + opcodes[instruction]
    except:
        # If there's any exception, handle it
        global error_Msg
        # If the global error message is empty, assign it the message "Invalid Instruction Format"
        if error_Msg == "": error_Msg = "Invalid Instruction Format"
        # Return None as the result
        return None

def parse_b_type(tokens):
    try:
        instruction, rs1, rs2, imm = tokens
        # Convert the immediate value to a binary string with a width of 16 bits
        bin_imm = to_bin(imm, 16)
        # Concatenate the binary representation parts according to RISC-V B-type format:
        # [immediate[12] | immediate[10:5] | rs2 | rs1 | funct3 | immediate[4:1] | immediate[11] | opcode]
        return bin_imm[3] + bin_imm[5:11] + bin_from_abi(rs2) + bin_from_abi(rs1) + funct3s[instruction] + bin_imm[11:15] + bin_imm[4] + opcodes[instruction]
    except:
        global error_Msg
        if error_Msg == "": error_Msg = "Invalid Instruction Format"
        return None

def parse_u_type(tokens):
    try:
        instruction, rd, imm = tokens
        # Convert the immediate value to a binary string with a width of 32 bits
        # Take the first 20 bits of the result
        return to_bin(imm, 32)[:20] + bin_from_abi(rd) + opcodes[instruction]
    except:
        global error_Msg
        if error_Msg == "": error_Msg = "Invalid Instruction Format"
        return None

# todo: recheck
def parse_j_type(tokens):
    try:
        # Extract the tokens from the input
        instruction, rd, imm = tokens
        # Convert the immediate value to a binary string with a width of 21 bits
        bin_imm = to_bin(imm, 21)
        # Concatenate the binary representation parts according to RISC-V J-type format:
        # [immediate[20] | immediate[10:1] | immediate[11] | immediate[19:12] | rd | opcode]
        return bin_imm[0] + bin_imm[-11:-1] + bin_imm[10] + bin_imm[1:9] + bin_from_abi(rd) + opcodes[instruction]
    except:
        # If there's any exception, handle it
        global error_Msg
        # If the global error message is empty, assign it the message "Invalid Instruction Format"
        if error_Msg == "": error_Msg = "Invalid Instruction Format"
        return None

def test_parsing():
    def tokenize(s):
        s = s.replace(',', ' ')
        s = s.replace('(', ' ')
        s = s.replace(')', '')
        tokens = s.split(' ')
        return tokens
    
    print(parse_j_type(tokenize("jal ra,-1024")) == "11000000000111111111000011101111")
    print(parse_b_type(tokenize("blt a4,a5,200")) == "00001100111101110100010001100011")
    print(parse_r_type(tokenize("add s1,s2,s3")) == "00000001001110010000010010110011")
    print(parse_i_type(tokenize("jalr ra,a5,-07")) == "11111111100101111000000011100111")
    print(parse_i_type(tokenize("lw a4,20(s1)")) == "00000001010001001010011100000011")
    print(parse_s_type(tokenize("sw ra,32(sp)")) == "00000010000100010010000000100011")
    print(parse_u_type(tokenize("auipc s2,-30")) == "11111111111111111111100100010111")

import sys

with open(sys.argv[1], 'r') as f:
    # read all the lines
    lines = []

    # Store the address of label definitions and line numbers
    lables_to_addr = {}
    lines_to_lineno = {}
    i = 0
    line_number = 0
    for line in f.readlines():
        line_number += 1
        if len(line.strip()) == 0: 
            continue # skip empty lines
        line = line.replace(',', ' ')
        line = line.replace('(', ' ')
        line = line.replace(')', '')
        # If found label...
        if len(line.split(':')) == 2:
            # ...remove it and store line address
            label, line = line.split(':')
            lables_to_addr[label] = i*4
        line = line.strip()

        lines_to_lineno[str(i)+line] = line_number # Ensure every line is unique by appending the line id
        lines.append(line)
        i += 1

    # Replace labels with appropriate address
    for i, line in enumerate(lines):
        for label, label_addr in lables_to_addr.items():
            if label in line.split(' '):
                line = line.replace(label, str((lables_to_addr[label] - i*4)))
        lines[i] = line

    # Write output file
    with open(sys.argv[2], 'w') as of:
        # Convert to binary
        hasVirtualHalt = False
        output = []
        for i, line in enumerate(lines):
            binary = None
            error_Msg = ""

            if line == "rst":
                binary = '00000000000000000000000001111111'
            elif line == "halt":
                binary = '11111111111111111111111111111111'
            else:
                # Tokenize and parse
                tokens = line.split()
                if tokens[0] == "rvrs":
                    instruction, rd, rs = tokens
                    binary = '0000000' + '00000' + bin_from_abi(rs) + '000' + bin_from_abi(rd) + '0000001'
                elif tokens[0] in types['R']: binary = parse_r_type(tokens)
                elif tokens[0] in types['I']: binary = parse_i_type(tokens)
                elif tokens[0] in types['S']: binary = parse_s_type(tokens)
                elif tokens[0] in types['B']: binary = parse_b_type(tokens)
                elif tokens[0] in types['U']: binary = parse_u_type(tokens)
                elif tokens[0] in types['J']: binary = parse_j_type(tokens)
                else: error_Msg = f"Invalid Instruction '{tokens[0]}'"
            
            # Print error
            if binary is None or error_Msg != "":
                print(f"ERROR: Line {lines_to_lineno[str(i)+line]}: {error_Msg}!")
                break
            
            # Keep track of wether or not we have found virtual halt instruction
            if binary == VIRTUAL_HALT_INSTRUCTION_BIN:
                hasVirtualHalt = True

            if i < len(lines) - 1:
                binary += "\n"
            output.append(binary)
        
        # Write to file only if we don't have any errors
        if not hasVirtualHalt and error_Msg == "":
            print("ERROR: Virtual Halt Not Found!")
        else:
            of.writelines(output)
