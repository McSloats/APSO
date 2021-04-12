
import metame.constants as constants

import re
import random
from keystone import *
from IPython import embed

class X86Handler:
    def get_nops(self, size, prev_ins_size=0):
        if self.bits == 32:
            regs = ["eax", "ebx", "ecx", "edx", "esi", "edi"]
        else:
            regs = ["rax", "rbx", "rcx", "rdx", "rsi", "rdi"]
        if size == 1:
            return "nop"
        elif size == 2 and self.bits == 32:
            r = random.randint(1, 3)
            if r == 1:
                reg = random.choice(regs)
                return "push %s; pop %s" % (reg, reg)
            elif r == 2:
                return "pushad; popad"
            elif r == 3:
                return "%s; %s" % (self.get_nops(1), self.get_nops(1))
        elif size == 3 and self.bits == 32:
            r = random.randint(1, 5)
            if r == 1:
                return "jmp %s; inc %s" % (3 + prev_ins_size, random.choice(regs))
            elif r == 2:
                return "jmp %s; push %s" % (3 + prev_ins_size, random.choice(regs))
            elif r == 3:
                return "jmp %s; pop %s" % (3 + prev_ins_size, random.choice(regs))
            elif r == 4:
                return "%s; %s" % (self.get_nops(1), self.get_nops(2))
            elif r == 5:
                return "%s; %s" % (self.get_nops(2), self.get_nops(1))
        elif size == 2 and self.bits == 64:
            reg = random.choice(regs)
            return "push %s; pop %s" % (reg, reg)
        elif size == 3 and self.bits == 64:
            r = random.randint(1, 4)
            if r == 1:
                reg = random.choice(regs)
                return "push %s; pop %s; %s" % (reg, reg, self.get_nops(1))
            elif r == 2:
                reg = random.choice(regs)
                return "%s; push %s; pop %s" % (self.get_nops(1), reg, reg)
            elif r == 3:
                return "%s; %s" % (self.get_nops(1), self.get_nops(2))
            elif r == 4:
                return "%s; %s" % (self.get_nops(2), self.get_nops(1))
        elif size == 4 and self.bits == 64:
            r = random.randint(1, 5)
            if r == 1:
                return "jmp %s; pop %s; pop %s" % (4 + prev_ins_size, random.choice(regs),
                                                   random.choice(regs))
            elif r == 2:
                return "jmp %s; push %s; push %s" % (4 + prev_ins_size, random.choice(regs),
                                                   random.choice(regs))
            elif r == 3:
                return "jmp %s; push %s; pop %s" % (4 + prev_ins_size, random.choice(regs),
                                                   random.choice(regs))
            elif r == 4:
                return "jmp %s; pop %s; push %s" % (4 + prev_ins_size, random.choice(regs),
                                                   random.choice(regs))
            elif r == 5:
                return "%s; %s" % (self.get_nops(2), self.get_nops(2))

    def __init__(self, bits, debug=False, force_replace=False):
        self.bits = bits
        self.debug = debug
        self.force = force_replace
        ks_mode = KS_MODE_32 if self.bits == 32 else KS_MODE_64
        self.ks = Ks(KS_ARCH_X86, ks_mode)
        self.init_mutations()

    def init_mutations(self):
        if self.bits == 32:
            self.mutables = frozenset(["nop","acmp","or","xor","sub","mov","push"])
            self.X86_SUBS = [
                (
                    ((re.compile(r"^mov (?P<a>e..), (?P<b>(?P=a))$"),), "mov {a}, {b}", True),
                    ((), "push eax; pop eax", False),
		    ((), "pop eax; push eax", False),
		    ((), "push ebx; pop ebx", False),
		    ((), "pop ebx; push ebx", False),
		    ((), "push ecx; pop ecx", False),
		    ((), "pop ecx; push ecx", False),
		    ((), "push edx; pop edx", False),
		    ((), "pop edx; push edx", False),
		    ((), "push esi; pop esi", False),
		    ((), "pop esi; push esi", False),
		    ((), "push edi; pop edi", False),
		    ((), "pop edi; push edi", False),
		    ((), "pushad; popad", False),
		    ((), "nop; nop", False),
                ),
                (
                    ((re.compile(r"^nop$"),re.compile(r"^nop$"),re.compile(r"^nop$")), "nop; nop; nop", True),
                    ((), "jmp %s; inc eax" % 3, False),
		    ((), "jmp %s; push eax" % 3, False),
		    ((), "jmp %s; pop eax" % 3, False),
		    ((), "nop; push eax; pop eax", False),
		    ((), "push eax; pop eax; nop", False),
		    ((), "jmp %s; inc ebx" % 3, False),
		    ((), "jmp %s; push ebx" % 3, False),
		    ((), "jmp %s; pop ebx" % 3, False),
		    ((), "nop; push ebx; pop ebx", False),
		    ((), "push ebx; pop ebx; nop", False),
		    ((), "jmp %s; inc ecx" % 3, False),
		    ((), "jmp %s; push ecx" % 3, False),
		    ((), "jmp %s; pop ecx" % 3, False),
		    ((), "nop; push ecx; pop ecx", False),
		    ((), "push ecx; pop ecx; nop", False),
		    ((), "jmp %s; inc edx" % 3, False),
		    ((), "jmp %s; push edx" % 3, False),
		    ((), "jmp %s; pop edx" % 3, False),
		    ((), "nop; push edx; pop edx", False),
		    ((), "push edx; pop edx; nop", False),
		    ((), "jmp %s; inc esi" % 3, False),
		    ((), "jmp %s; push esi" % 3, False),
		    ((), "jmp %s; pop esi" % 3, False),
		    ((), "nop; push esi; pop esi", False),
		    ((), "push esi; pop esi; nop", False),
		    ((), "jmp %s; inc edi" % 3, False),
		    ((), "jmp %s; push edi" % 3, False),
		    ((), "jmp %s; pop edi" % 3, False),
		    ((), "nop; push edi; pop edi", False),
		    ((), "push edi; pop edi; nop", False),
		    ((), "pushad; popad; nop", False),
		    ((), "nop; pushad; popad", False),
		    ((), "nop; nop; nop", False),
                ),
                (
                    ((re.compile(r"^nop$"),re.compile(r"^nop$")), "nop; nop", True),
                    ((), "push eax; pop eax", False),
		    ((), "pop eax; push eax", False),
		    ((), "push ebx; pop ebx", False),
		    ((), "pop ebx; push ebx", False),
		    ((), "push ecx; pop ecx", False),
		    ((), "pop ecx; push ecx", False),
		    ((), "push edx; pop edx", False),
		    ((), "pop edx; push edx", False),
		    ((), "push esi; pop esi", False),
		    ((), "pop esi; push esi", False),
		    ((), "push edi; pop edi", False),
		    ((), "pop edi; push edi", False),
		    ((), "pushad; popad", False),
		    ((), "nop; nop", False),
                ),
                (
                    ((re.compile(r"^test (?P<a>e..), (?P<b>(?P=a))$"),), "test {a}, {b}", True),
                    ((re.compile(r"^or (?P<a>e..), (?P<b>(?P=a))$"),), "or {a}, {b}", True),
                ),
                (
                    ((re.compile(r"^xor (?P<a>e..), (?P<b>(?P=a))$"),), "xor {a}, {b}", True),
                    ((re.compile(r"^sub (?P<a>e..), (?P<b>(?P=a))$"),), "sub {a}, {b}", True),
                ),
                (
                    ((re.compile(r"^mov (?P<a>e..), (?P<b>e..)$"),), "mov {a}, {b}", True),
                    ((re.compile(r"^push (?P<b>e..)$"),re.compile(r"^pop (?P<a>e..)$")), "push {b}; pop {a}", True),
                ),
                (
                    ((re.compile(r"^mov (?P<a>e..), (?P<b>0?x?0)$"),), "mov {a}, {b}", True),
                    ((), "pushfd; xor {a}, {a}; popfd; %s" % self.get_nops(1), False),
                    ((), "pushfd; sub {a}, {a}; popfd; %s" % self.get_nops(1), False),
                    ((), "pushfd; and {a}, 0; popfd", False),
                ),
                (
                    ((re.compile(r"^mov (?P<a>e..), (?P<b>0?x?1)$"),), "mov {a}, {b}", True),
                    ((), "pushfd; xor {a}, {a}; inc {a}; popfd", False),
                ),
                (
                    ((re.compile(r"^mov (?P<a>e..), (?P<b>0?x?([0-7][0-9A-Fa-f]|[0-9A-Fa-f]))$"),), "mov {a}, {b}", True),
                    ((), "push {b}; pop {a}; push eax; pop eax", False),
		    ((), "push {b}; pop {a}; pop eax; push eax", False),
		    ((), "push {b}; pop {a}; push ebx; pop ebx", False),
		    ((), "push {b}; pop {a}; pop ebx; push ebx", False),
		    ((), "push {b}; pop {a}; push ecx; pop ecx", False),
		    ((), "push {b}; pop {a}; pop ecx; push ecx", False),
		    ((), "push {b}; pop {a}; push edx; pop edx", False),
		    ((), "push {b}; pop {a}; pop edx; push edx", False),
		    ((), "push {b}; pop {a}; push esi; pop esi", False),
		    ((), "push {b}; pop {a}; pop esi; push esi", False),
		    ((), "push {b}; pop {a}; push edi; pop edi", False),
		    ((), "push {b}; pop {a}; pop edi; push edi", False),
		    ((), "push {b}; pop {a}; pushad; popad", False),
		    ((), "push {b}; pop {a}; nop; nop", False),
                    ((), "push eax; pop eax; push {b}; pop {a}", False),
		    ((), "pop eax; push eax; push {b}; pop {a}", False),
		    ((), "push ebx; pop ebx; push {b}; pop {a}", False),
		    ((), "pop ebx; push ebx; push {b}; pop {a}", False),
		    ((), "push ecx; pop ecx; push {b}; pop {a}", False),
		    ((), "pop ecx; push ecx; push {b}; pop {a}", False),
		    ((), "push edx; pop edx; push {b}; pop {a}", False),
		    ((), "pop edx; push edx; push {b}; pop {a}", False),
		    ((), "push esi; pop esi; push {b}; pop {a}", False),
		    ((), "pop esi; push esi; push {b}; pop {a}", False),
		    ((), "push edi; pop edi; push {b}; pop {a}", False),
		    ((), "pop edi; push edi; push {b}; pop {a}", False),
		    ((), "pushad; popad; push {b}; pop {a}", False),
		    ((), "nop; nop; push {b}; pop {a}", False),
                    ((), "%s; push {b}; %s; pop {a}" % (self.get_nops(1), self.get_nops(1)), False),
                ),
            ]
        else:
            self.mutables = frozenset(["nop","acmp","or","xor","sub","mov"])
            self.X86_SUBS = [
                # Variations of 32 bits payloads
                (
                    ((re.compile(r"^mov (?P<a>e..), (?P<b>(?P=a))$"),), "mov {a}, {b}", True),
                    ((), "push eax; pop eax", False),
		    ((), "pop eax; push eax", False),
		    ((), "push ebx; pop ebx", False),
		    ((), "pop ebx; push ebx", False),
		    ((), "push ecx; pop ecx", False),
		    ((), "pop ecx; push ecx", False),
		    ((), "push edx; pop edx", False),
		    ((), "pop edx; push edx", False),
		    ((), "push esi; pop esi", False),
		    ((), "pop esi; push esi", False),
		    ((), "push edi; pop edi", False),
		    ((), "pop edi; push edi", False),
		    ((), "pushad; popad", False),
           	    ((), "nop; nop", False),
                ),
                (
                    ((re.compile(r"^nop$"),re.compile(r"^nop$"),re.compile(r"^nop$")), "nop; nop; nop", True),
                    ((), "jmp %s; inc eax" % 3, False),
		    ((), "jmp %s; push eax" % 3, False),
		    ((), "jmp %s; pop eax" % 3, False),
		    ((), "nop; push eax; pop eax", False),
		    ((), "push eax; pop eax; nop", False),
		    ((), "jmp %s; inc ebx" % 3, False),
		    ((), "jmp %s; push ebx" % 3, False),
		    ((), "jmp %s; pop ebx" % 3, False),
		    ((), "nop; push ebx; pop ebx", False),
		    ((), "push ebx; pop ebx; nop", False),
		    ((), "jmp %s; inc ecx" % 3, False),
		    ((), "jmp %s; push ecx" % 3, False),
		    ((), "jmp %s; pop ecx" % 3, False),
		    ((), "nop; push ecx; pop ecx", False),
		    ((), "push ecx; pop ecx; nop", False),
		    ((), "jmp %s; inc edx" % 3, False),
		    ((), "jmp %s; push edx" % 3, False),
		    ((), "jmp %s; pop edx" % 3, False),
		    ((), "nop; push edx; pop edx", False),
		    ((), "push edx; pop edx; nop", False),
		    ((), "jmp %s; inc esi" % 3, False),
		    ((), "jmp %s; push esi" % 3, False),
		    ((), "jmp %s; pop esi" % 3, False),
		    ((), "nop; push esi; pop esi", False),
		    ((), "push esi; pop esi; nop", False),
		    ((), "jmp %s; inc edi" % 3, False),
		    ((), "jmp %s; push edi" % 3, False),
		    ((), "jmp %s; pop edi" % 3, False),
		    ((), "nop; push edi; pop edi", False),
		    ((), "push edi; pop edi; nop", False),
		    ((), "pushad; popad; nop", False),
		    ((), "nop; pushad; popad", False),
		    ((), "nop; nop; nop", False),
                ),
                (
                    ((re.compile(r"^nop$"),re.compile(r"^nop$")), "nop; nop", True),
                    ((), "push eax; pop eax", False),
		    ((), "pop eax; push eax", False),
		    ((), "push ebx; pop ebx", False),
		    ((), "pop ebx; push ebx", False),
		    ((), "push ecx; pop ecx", False),
		    ((), "pop ecx; push ecx", False),
		    ((), "push edx; pop edx", False),
		    ((), "pop edx; push edx", False),
		    ((), "push esi; pop esi", False),
		    ((), "pop esi; push esi", False),
		    ((), "push edi; pop edi", False),
		    ((), "pop edi; push edi", False),
		    ((), "pushad; popad", False),
    		    ((), "nop; nop", False),
                ),
                (
                    ((re.compile(r"^test (?P<a>e..), (?P<b>(?P=a))$"),), "test {a}, {b}", True),
                    ((re.compile(r"^or (?P<a>e..), (?P<b>(?P=a))$"),), "or {a}, {b}", True),
                ),
                (
                    ((re.compile(r"^xor (?P<a>e..), (?P<b>(?P=a))$"),), "xor {a}, {b}", True),
                    ((re.compile(r"^sub (?P<a>e..), (?P<b>(?P=a))$"),), "sub {a}, {b}", True),
                ),
                # Purely 64 bits payloads
                (
                    ((re.compile(r"^test (?P<a>r..), (?P<b>(?P=a))$"),), "test {a}, {b}", True),
                    ((re.compile(r"^or (?P<a>r..), (?P<b>(?P=a))$"),), "or {a}, {b}", True),
                ),
                (
                    ((re.compile(r"^xor (?P<a>r..), (?P<b>(?P=a))$"),), "xor {a}, {b}", True),
                    ((re.compile(r"^sub (?P<a>r..), (?P<b>(?P=a))$"),), "sub {a}, {b}", True),
                ),
                (
                    ((re.compile(r"^mov (?P<a>r.(i|x|p)), (?P<b>r.(i|x|p))$"),), "mov {a}, {b}", True),
                    ((), "push {b}; pop {a}; %s" % self.get_nops(1), False),
                    ((), "%s; push {b}; pop {a}" % self.get_nops(1), False),
                    ((), "push {b}; %s; pop {a}" % self.get_nops(1), False),
                ),
            ]

    def assemble_code(self, codestr):
        encoding, count = self.ks.asm(codestr)
        return "".join(["%02x" % i for i in encoding])

    def replace_fcn_opcodes(self, fcn_ctx):
        replacements = []
        # Iternate instructions
        count = -1
        n_ops = len(fcn_ctx["ops"])
        while count < n_ops-1:
            count += 1
            if fcn_ctx["ops"][count].get("type") not in self.mutables:
                continue
            # Iternate possible substitutions
            for x86_sub in self.X86_SUBS:
                # Iterate equivalences in substitution
                for x86_find in x86_sub:
                    # Use this equivalence as match, or only as replacement?
                    if not x86_find[2]:
                        continue
                    count_2 = 0
                    ms = []
                    opcodes_len = 0
                    # Iterate needed matches
                    for x86_m in x86_find[0]:
                        try:
                            # Match
                            m = x86_m.match(fcn_ctx["ops"][count+count_2]["opcode"])
                            if not m:
                                break
                            else:
                                print("Match: "+str(fcn_ctx["ops"][count].get("opcode")))
                        except:
                                break
                        # Store matches
                        ms.append(m)
                        # Increase opcodes size
                        opcodes_len += len(fcn_ctx["ops"][count+count_2]["bytes"])
                        count_2 += 1
                    else:
                        # Previous iteration was completed, so all needed matches matched
                        # Choose a random substitution
                        counter = 0
                        for sub in x86_sub:
                        #sub = random.choice(x86_sub)
                        # If forced, force finding a different substitution
                        #while self.force and sub == x86_find:
                        #    sub = random.choice(x86_sub)
                        # Random substitution is the same, do nothing
                            counter += 1
                            if sub == x86_find:
                                continue
                            res_ass = sub[1]
                            # Create assembly replacing match groups
                            for m in ms:
                                for idx in m.groupdict().keys():
                                    res_ass = res_ass.replace("{%s}" % idx, m.groupdict()[idx])
                            if self.debug:
                                print("[DEBUG] Replacing instruction at %s (%s) with: %s ... " % (
                                        hex(fcn_ctx["ops"][count]["offset"]),
                                        fcn_ctx["ops"][count]["opcode"],
                                        res_ass))
                            # Assemble new code
                            new_assembly = self.assemble_code(res_ass)
                            # Check if new assembly is equal in size
                            if len(new_assembly) == opcodes_len:
                                replacements.append({"offset": fcn_ctx["ops"][count]["offset"],
                                                     "newbytes": res_ass})
                                print({"offset": fcn_ctx["ops"][count]["offset"],
                                                     "newbytes": res_ass})
                                if len(x86_sub) == counter:
                                # Avoid patching over again
                                    count += count_2 - 1
                                # Restart mutations to reseed random nops
                                #self.init_mutations()
                                #break
                            else:
                                if self.debug:
                                    print("[DEBUG] Instruction opcodes are different in size")
                else:
                    # Previous iteration failed, continue finding substitutions
                    # for this instruction
                    continue
                # Previous iteration was completed correctly, stop
                # finding substitutions for this instruction
                #break
        return replacements

