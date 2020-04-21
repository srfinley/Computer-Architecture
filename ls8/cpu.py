"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0

        self.branchtable = {}
        self.branchtable[1] = self.HLT
        self.branchtable[130] = self.LDI
        self.branchtable[71] = self.PRN
        self.branchtable[162] = self.MUL
        

    def load(self, filename):
        """Load a program into memory."""

        address = 0

        # loads the first word in a line if it starts with 1/0
        with open(filename) as f:
            for line in f:
                words = line.split()
                if len(words) > 0:
                    if words[0][0] == "1" or words[0][0] == "0":
                        self.ram[address] = int(words[0], 2)
                        address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

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

    def MUL(self, address1, address2):
        """Multiplies values in address1 by that in address2"""
        self.alu("MUL", address1, address2)

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
            self.pc += advance
