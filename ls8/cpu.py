"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0

        # the register R7 points to the top of the stack
        self.SP_reg = 7
        self.reg[self.SP_reg] = 244

        self.branchtable = {}
        self.branchtable[1] = self.HLT
        self.branchtable[130] = self.LDI
        self.branchtable[71] = self.PRN

        self.branchtable[69] = self.PUSH
        self.branchtable[70] = self.POP

        self.branchtable[84] = self.JMP

        self.branchtable[101] = lambda a, b: self.alu('INC', a, b)
        self.branchtable[102] = lambda a, b: self.alu('DEC', a, b)
        self.branchtable[160] = lambda a, b: self.alu('ADD', a, b)
        self.branchtable[161] = lambda a, b: self.alu('SUB', a, b)
        self.branchtable[162] = lambda a, b: self.alu('MUL', a, b)
        self.branchtable[163] = lambda a, b: self.alu('DIV', a, b)
        self.branchtable[164] = lambda a, b: self.alu('MOD', a, b)

        self.branchtable[168] = lambda a, b: self.alu('AND', a, b)
        self.branchtable[170] = lambda a, b: self.alu('OR', a, b)
        self.branchtable[171] = lambda a, b: self.alu('XOR', a, b)
        self.branchtable[172] = lambda a, b: self.alu('SHL', a, b)
        self.branchtable[173] = lambda a, b: self.alu('SHR', a, b)
        

    def load(self, argv):
        """Load a program into memory."""
        try:
            filename = argv[1]
        except IndexError:
            print("Must include a filepath as an argument")
            sys.exit()

        address = 0

        # loads the first word in a line if it starts with 1/0
        with open(filename) as f:
            for line in f:
                words = line.split()
                if len(words) > 0:
                    if words[0][0] == "1" or words[0][0] == "0":
                        self.ram_write(address, int(words[0], 2))
                        address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        operations = {
            "ADD": lambda: self.reg[reg_a] + self.reg[reg_b],
            "SUB": lambda: self.reg[reg_a] - self.reg[reg_b],
            "MUL": lambda: self.reg[reg_a] * self.reg[reg_b],
            "DIV": lambda: self.reg[reg_a] // self.reg[reg_b],
            "MOD": lambda: self.reg[reg_a] % self.reg[reg_b],
            "DEC": lambda: self.reg[reg_a] - 1,
            "INC": lambda: self.reg[reg_a] + 1,

            "AND": lambda: self.reg[reg_a] & self.reg[reg_b],
            "OR": lambda: self.reg[reg_a] | self.reg[reg_b],
            "XOR": lambda: self.reg[reg_a] ^ self.reg[reg_b],
            "SHL": lambda: self.reg[reg_a] << self.reg[reg_b],
            "SHR": lambda: self.reg[reg_a] >> self.reg[reg_b],
        }

        # HANDLE CMP WITH DEFINED FUNCTION THAT RETURNS ORIGINAL VALUE
        try:
            self.reg[reg_a] = (operations[op]() & 0xFF)
        except ZeroDivisionError:
            print("Attempt to divide by zero")
            sys.exit()
        except KeyError:
            raise Exception(f"Unsupported ALU operation: {op}")


    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, MAR):
        """Returns the value stored at the Memory Address Register"""
        MDR = self.ram[MAR]
        return MDR

    def ram_write(self, MAR, MDR):
        """Writes the Memory Data Register to the Memory Address Register"""
        self.ram[MAR] = MDR

    def PRN(self, address, _):
        """Function 71, prints value from address"""
        print(self.reg[address])

    def LDI(self, address, value):
        """Function 130, saves value to register address"""
        self.reg[address] = value

    def HLT(self, *args):
        """Halts the program"""
        sys.exit()

    def PUSH(self, address, _):
        """Puts the item from the reg address onto the stack"""

        # decrement stack pointer
        self.alu("DEC", self.SP_reg, _)

        # add value at address to RAM at the pointed-to place
        self.ram_write(self.reg[self.SP_reg], self.reg[address])

    def POP(self, address, _):
        """Puts item from top of stack into address"""
        
        # copy the value at the top of the stack to address
        self.LDI(address, self.ram_read(self.reg[self.SP_reg]))

        # increment stack pointer
        self.alu("INC", self.SP_reg, _)

    def JMP(self, address, _):
        """Move PC to RAM location stored at reg address"""
        self.pc = self.reg[address]

    def run(self):
        """Run the CPU."""
        while True:
            IR = self.ram_read(self.pc)

            # first two bits are the number of args
            # pc will advance by that much plus one
            advance = (IR >> 6) + 1

            # still a lil concerned about assigning a command as an operand
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            self.branchtable[IR](operand_a, operand_b)

            # fourth bit is whether the command sets the PC
            # mask with & to isolate the bit and shift
            if not ((IR & 0b00010000) >> 4):
                self.pc += advance
