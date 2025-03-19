import sys
import reversesim

in_file, out_file = sys.argv[1], sys.argv[2]
VIRTUAL_HALT_INSTRUCTION_BIN = "00000000000000000000000001100011"

def to_dec(binary, unsigned=False):
    if '0b' in binary:
        binary = binary[2:]
    if not unsigned and binary[0] == "1":
        inverted_binary = "".join(["1" if bit == "0" else "0" for bit in binary])
        decimal_number = int(inverted_binary, 2) + 1
        return -decimal_number
    else:
        return int(binary, 2)

def to_bin(n, bits):
    bstr = None
    n = int(n)
    bstr = bin(n & int("1"*bits, 2))[2:]
    padded = bstr.zfill(bits)
    return str(padded)

# store the instructions {int -> 32bin}
program_memory = {}
with open(in_file) as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        program_memory[i*4] = line.strip()

program_counter = 0

# stack memory {5bin -> 32bin}
registers = {}
for i in range(32):
    registers[format(i, '05b')] = format(0, '032b')
registers['00010'] = format(256, '032b') # sp

# data memory {8hex -> 32bin}
data_memory = {}
for i in range(0x10000, 0x1007F, 4):
    data_memory[format(i, '08x')] = format(0, '032b')

def execute_r_type(instruction: str):
    global program_counter
    funct7 = instruction[:7]
    rs2 = instruction[7:12]
    rs1 = instruction[12:17]
    funct3 = instruction[17:20]
    rd = instruction[20:25]

    rs1_int, rs2_int, rs1_uint, rs2_uint = to_dec(registers[rs1]), to_dec(registers[rs2]), to_dec(registers[rs1], True), to_dec(registers[rs2], True)

    result = None

    if funct3 == '000':
        if funct7 == '0000000': # x[rd] = x[rs1] + x[rs2]
            result = rs1_int + rs2_int
            print('add', reversesim.bin_to_abi(rd), reversesim.bin_to_abi(rs1), reversesim.bin_to_abi(rs2), result)
        else: # x[rd] = x[rs1] - x[rs2]
            result = rs1_int - rs2_int
            print('sub', reversesim.bin_to_abi(rd), reversesim.bin_to_abi(rs1), reversesim.bin_to_abi(rs2), result)
    elif funct3 == '001': # x[rd] = x[rs1] << x[rs2] (lower 5 bits)
        result = rs1_int << to_dec(registers[rs2][-5:], True)
        print('sll', reversesim.bin_to_abi(rd), reversesim.bin_to_abi(rs1), reversesim.bin_to_abi(rs2, True), result)
    elif funct3 == '010': # x[rd] = x[rs1] <s x[rs2]
        result = 1 if rs1_int < rs2_int else 0
        print('slt', reversesim.bin_to_abi(rd), reversesim.bin_to_abi(rs1), reversesim.bin_to_abi(rs2), result)
    elif funct3 == '011': # x[rd] = x[rs1] <u x[rs2]
        result = 1 if rs1_uint < rs2_uint else 0
        print('sltu', reversesim.bin_to_abi(rd), reversesim.bin_to_abi(rs1, True), reversesim.bin_to_abi(rs2, True), result)
    elif funct3 == '100': # x[rd] = x[rs1] ^ x[rs2]
        result = rs1_int ^ rs2_int
        print('xor', reversesim.bin_to_abi(rd), reversesim.bin_to_abi(rs1), reversesim.bin_to_abi(rs2), result)
    elif funct3 == '101': # x[rd] = x[rs1] >>u x[rs2] (lower 5 bits)
        result = rs1_int >> to_dec(registers[rs2][-5:], True)
        print('srl', reversesim.bin_to_abi(rd), reversesim.bin_to_abi(rs1), reversesim.bin_to_abi(rs2, True), result)
    elif funct3 == '110': # x[rd] = x[rs1] | x[rs2]
        result = rs1_int | rs2_int
        print('or', reversesim.bin_to_abi(rd), reversesim.bin_to_abi(rs1), reversesim.bin_to_abi(rs2), result)
    elif funct3 == '111':
        if funct7 == '0000000': # x[rd] = x[rs1] & x[rs2]
            result = rs1_int & rs2_int
            print('and', reversesim.bin_to_abi(rd), reversesim.bin_to_abi(rs1), reversesim.bin_to_abi(rs2), result)
        else: # BONUS: # x[rd] = x[rs1] * x[rs2]
            result = rs1_int * rs2_int
            print('mul', reversesim.bin_to_abi(rd), reversesim.bin_to_abi(rs1), reversesim.bin_to_abi(rs2), result)
    
    program_counter += 4

    registers[rd] = to_bin(result, 32)
    # if funct7 != '0000000' and funct3 == '000': # sub
    #     print(f'{rs1_int} - {rs2_int} = {result} : storing in x{int(rd,2)} : reg is {registers[rd]}')

def execute_i_type(instruction: str):
    global program_counter
    opcode = instruction[-7:]
    imm = instruction[-32:-20]
    rs1 = instruction[-20:-15]
    funct3 = instruction[-15:-12]
    rd = instruction[-12:-7]

    rs1_int = to_dec(registers[rs1])
    result = None

    if funct3 == '010' and opcode == '0000011': # lw
        mem_addr = rs1_int + to_dec(imm)
        result = to_dec(data_memory[format(mem_addr, '08x')])
        program_counter += 4
        print('lw', reversesim.bin_to_abi(rd), reversesim.bin_to_abi(rs1), to_dec(imm), result)
    elif funct3 == '000' and opcode == '0010011': # addi
        result = rs1_int + to_dec(imm)
        program_counter += 4
        print('addi', reversesim.bin_to_abi(rd), reversesim.bin_to_abi(rs1), to_dec(imm), result)
    elif funct3 == '011' and opcode == '0010011': # sltiu
        result = 1 if to_dec(registers[rs1], True) < to_dec(imm, True) else 0
        print('sltiu', reversesim.bin_to_abi(rd), reversesim.bin_to_abi(rs1), to_dec(imm), result)
        program_counter += 4
    elif funct3 == '000' and opcode == '1100111': # jalr
        result = program_counter + 4
        program_counter = (rs1_int + to_dec(imm))
        print('jalr', reversesim.bin_to_abi(rd), reversesim.bin_to_abi(rs1), to_dec(imm), result)

    registers[rd] = to_bin(result, 32)

def execute_s_type(instruction: str):
    imm = instruction[:7] + instruction[20:25]
    rs2 = instruction[7:12]
    rs1 = instruction[12:17]
    # sw
    mem_addr = to_dec(registers[rs1]) + to_dec(imm)
    data_memory[format(mem_addr, '08x')] = registers[rs2]
    print('sw', reversesim.bin_to_abi(rs2), f'{to_dec(imm)}({reversesim.bin_to_abi(rs1)})', mem_addr)
    global program_counter
    program_counter += 4

def execute_b_type(instruction: str):
    global program_counter
    imm = instruction[0] + instruction[24] + instruction[1:7] + instruction[20:24] + '0'
    rs2 = instruction[7:12]
    rs1 = instruction[12:17]
    funct3 = instruction[17:20]

    rs1_int, rs2_int, rs1_uint, rs2_uint = to_dec(registers[rs1]), to_dec(registers[rs2]), to_dec(registers[rs1], True), to_dec(registers[rs2], True)
    imm_int, imm_uint = to_dec(imm), to_dec(imm, True)

    if cur_instruction == VIRTUAL_HALT_INSTRUCTION_BIN:
        print("VIRTUAL HALT")
        return

    if funct3 == '000': # if (x[rs1] == x[rs2]) pc += sext(offset)
        if rs1_int == rs2_int:
            program_counter += imm_int
        else:
            program_counter += 4
        print('beq', reversesim.bin_to_abi(rs1), reversesim.bin_to_abi(rs2), imm_int, rs1_int == rs2_int)
    elif funct3 == '001': # if (x[rs1] != x[rs2]) pc += sext(offset)
        if rs1_int != rs2_int:
            program_counter += imm_int
        else:
            program_counter += 4
        print('bne', reversesim.bin_to_abi(rs1), reversesim.bin_to_abi(rs2), imm_int, rs1_int != rs2_int)
    elif funct3 == '100': # if (x[rs1] < x[rs2]) pc += sext(offset)
        if rs1_int < rs2_int:
            program_counter += imm_int
        else:
            program_counter += 4
        print('blt', reversesim.bin_to_abi(rs1), reversesim.bin_to_abi(rs2), imm_int, rs1_int < rs2_int)
    elif funct3 == '101': # if (x[rs1] >= x[rs2]) pc += sext(offset)
        if rs1_int >= rs2_int:
            program_counter += imm_int
        else:
            program_counter += 4
        print('bge', reversesim.bin_to_abi(rs1), reversesim.bin_to_abi(rs2), imm_int, rs1_int >= rs2_int)
    elif funct3 == '110': # if (x[rs1] <u x[rs2]) pc += sext(offset)
        if rs1_uint < rs2_uint:
            program_counter += imm_uint
        else:
            program_counter += 4
        print('bltu', reversesim.bin_to_abi(rs1, True), reversesim.bin_to_abi(rs2, True), imm_int, rs1_uint < rs2_uint)
    elif funct3 == '111': # if (x[rs1] >=u x[rs2]) pc += sext(offset)
        if rs1_uint >= rs2_uint:
            program_counter += imm_uint
        else:
            program_counter += 4
        print('bgeu', reversesim.bin_to_abi(rs1, True), reversesim.bin_to_abi(rs2, True), imm_int, rs1_uint >= rs2_uint)

def execute_u_type(instruction: str):
    global program_counter
    opcode = instruction[-7:]
    imm = instruction[:20] + format(0, '012b')
    rd = instruction[20:25]

    result = None

    if opcode == "0110111": # x[rd] = sext(immediate[31:12] << 12)
        result = to_dec(imm)
        print('lui', reversesim.bin_to_abi(rd), to_dec(instruction[:20]), result)
    else: # x[rd] = pc + sext(immediate[31:12] << 12)
        result = program_counter + to_dec(imm)
        print('auipc', reversesim.bin_to_abi(rd), to_dec(instruction[:20]), result)

    program_counter += 4
    registers[rd] = to_bin(result, 32)

def execute_j_type(instruction: str):
    imm = instruction[0] + instruction[12:20] + instruction[11] + instruction[1:11] + '0'
    rd = instruction[20:25]

    global program_counter
    result = program_counter + 4
    program_counter = program_counter + to_dec(imm)

    print('jal', reversesim.bin_to_abi(rd), to_dec(imm), result, program_counter)

    registers[rd] = to_bin(result, 32)


out_string = ""

def print_registers():
    global out_string
    out_string += "0b" + format(program_counter, '032b') + " "
    for i, reg_data in enumerate(registers.values()):
        out_string += "0b" + reg_data + " "
    out_string += "\n"


i = 0
while True:
    i += 1
    cur_instruction = program_memory[program_counter]
    reversesim.reg_mem = registers
    print(f"#{i:02d} {program_counter:02d}", end=": ")

    opcode = cur_instruction[-7:]
    # if cur_instruction == "00000000000000000000000001100011":
    #     print("HALT")
    #     break

    # BOUNS
    if cur_instruction == "00000000000000000000000001111111": # rst
        for i in range(32):
            registers[format(i, '05b')] = format(0, '032b')
        registers['00010'] = format(256, '032b')
        print("rst", [val == format(0, '032b') for i, val in enumerate(registers.values()) if i != 2] == [True]*31)
        program_counter += 4
    # BOUNS
    elif cur_instruction == "11111111111111111111111111111111": # halt
        print("halt")
        print_registers()
        break
    # BONUS
    elif opcode == '0000001': # rvrs rd, rs1
        rd = cur_instruction[-12:-7]
        rs1 = cur_instruction[-20:-15]
        registers[rd] = registers[rs1][::-1]
        print('rvrs', reversesim.bin_to_abi(rd), reversesim.bin_to_abi(rs1), registers[rd])
        program_counter += 4
    elif opcode == "0110011": # R-type
        execute_r_type(cur_instruction)
    elif opcode == "0000011" or opcode == "0010011" or opcode == "1100111": # I-type
        execute_i_type(cur_instruction)
    elif opcode == "0100011": # S-type
        execute_s_type(cur_instruction)
    elif opcode == "1100011": # B-type
        execute_b_type(cur_instruction)
    elif opcode == "0010111" or opcode == "0110111": # U-type
        execute_u_type(cur_instruction)
    elif opcode == "1101111": # J-type
        execute_j_type(cur_instruction)

    registers['00000'] = format(0, '032b') # x0 is hardwired to 0
    
    print_registers()
    # print(i, out_string.strip().split('\n')[-1].split()[20] if len(out_string.split('\n')) > 1 else "")
    # print x19 

    if cur_instruction == VIRTUAL_HALT_INSTRUCTION_BIN:
        break

for addr, data in data_memory.items():
    out_string += "0x" + addr + ":0b" + data + "\n"

with open(out_file, "w") as f:
    f.write(out_string)